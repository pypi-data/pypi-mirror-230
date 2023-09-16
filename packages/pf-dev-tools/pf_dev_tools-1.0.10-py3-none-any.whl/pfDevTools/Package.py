#
# Copyright (c) 2023-present Didier Malenfant
#
# This file is part of pfDevTools.
#
# pfDevTools is free software: you can redistribute it and/or modify it under the terms of the GNU General
# Public License as published by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pfDevTools is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the
# implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public
# License for more details.
#
# You should have received a copy of the GNU General Public License along with pfDevTools. If not,
# see <https://www.gnu.org/licenses/>.
#

import os
import sys
import shutil
import zipfile
import traceback
import pfDevTools

from typing import List
from pathlib import Path
from datetime import date

from .Exceptions import ArgumentError


# -- Classes
class Package:
    """A tool to package an analog pocket core"""

    @classmethod
    def _writeStringEntryFromValue(cls, file, entry_name: str, value, end_comma: bool = True, extra_spaces: str = ''):
        if value is None:
            return

        string_version: str = f'"{value}"' if value.startswith('0x') else value
        comma_string: str = ',' if end_comma else ''

        file.write(f'        {extra_spaces}"{entry_name}": {string_version}{comma_string}\n')

    @classmethod
    def _writeBooleanEntryFromValue(cls, file, entry_name: str, value: bool, end_comma: bool = True, extra_spaces: str = ''):
        if value is None:
            return

        string_version: str = "true" if value else "false"
        comma_string: str = ',' if end_comma else ''

        file.write(f'        {extra_spaces}"{entry_name}": {string_version}{comma_string}\n')

    def __init__(self, arguments, debug_on: bool = False):
        """Constructor based on command line arguments."""

        self._debug_on: bool = debug_on

        if len(arguments) != 3:
            raise ArgumentError('Invalid arguments. Maybe start with `pf --help?')

        self._config = pfDevTools.CoreConfig(arguments[0])
        self._destination_folder: str = arguments[1]
        self._packaging_folder: str = os.path.join(self._destination_folder, '_core')
        self._cores_folder: str = os.path.join(self._packaging_folder, 'Cores', self._config.fullPlatformName())
        self._platforms_folder: str = os.path.join(self._packaging_folder, 'Platforms')
        self._platforms_images_folder = os.path.join(self._platforms_folder, '_images')

        self._today = str(date.today())
        if len(self._today) > 10:
            raise ArgumentError(f'Internal error generating today\'s date \'{self._today}\'. Maximum length is 10 characters.')

        self._bitstream_files: List[str] = []
        for core_id in self._config.coresList():
            self._bitstream_files.append([os.path.join(arguments[2], self._config.coreSourceFile(core_id)), self._config.coreFilename(core_id)])

    def _generateDataFile(self) -> None:
        with open(os.path.join(self._cores_folder, 'data.json'), 'w') as out_file:
            out_file.write('{\n')
            out_file.write('  "data": {\n')
            out_file.write('    "magic": "APF_VER_1",\n')
            out_file.write('    "data_slots": [')

            found_a_slot: bool = False
            for slot_id in self._config.fileSlotList():
                if found_a_slot is True:
                    out_file.write(',')

                out_file.write('\n      {\n')
                out_file.write(f'        "name": "{self._config.fileSlotName(slot_id)}",\n')
                out_file.write(f'        "id": {slot_id},\n')
                Package._writeBooleanEntryFromValue(out_file, 'required', self._config.fileSlotRequired(slot_id))
                out_file.write(f'        "parameters": {self._config.fileSlotParameters(slot_id)},\n')

                Package._writeBooleanEntryFromValue(out_file, 'deferload', self._config.fileSlotDeferLoad(slot_id))
                Package._writeBooleanEntryFromValue(out_file, 'secondary', self._config.fileSlotSecondary(slot_id))
                Package._writeBooleanEntryFromValue(out_file, 'nonvolatile', self._config.fileSlotNonVolatile(slot_id))

                # TODO: If this is specified then the file needs to be potentially converted and then put in the right spot in the core package
                # filename: str = self._config.fileSlotFilename(slot_id)
                # if filename is not None:
                #    out_file.write(f'          "filename": "{filename}",\n')

                extensions: List[str] = self._config.fileSlotExtensions(slot_id)
                if len(extensions) != 0:
                    out_file.write('        "extensions": [\n')
                    for extension in extensions:
                        out_file.write(f'            "{extension}"\n')
                    out_file.write('        ],\n')

                Package._writeStringEntryFromValue(out_file, 'size_exact', self._config.fileSlotRequiredSize(slot_id))
                Package._writeStringEntryFromValue(out_file, 'size_maximum', self._config.fileSlotMaximumSize(slot_id))
                Package._writeStringEntryFromValue(out_file, 'address', self._config.fileSlotAddress(slot_id))

                out_file.write('      }')

                found_a_slot = True

            if found_a_slot:
                out_file.write('\n    ')

            out_file.write(']\n')
            out_file.write('  }\n')
            out_file.write('}\n')

    def _generateInteractFile(self) -> None:
        with open(os.path.join(self._cores_folder, 'interact.json'), 'w') as out_file:
            out_file.write('{\n')
            out_file.write('  "interact": {\n')
            out_file.write('    "magic": "APF_VER_1",\n')
            out_file.write('    "variables": [')

            found_a_variable: bool = False
            for variable_id in self._config.variableList():
                if found_a_variable is True:
                    out_file.write(',')

                out_file.write('\n      {\n')

                out_file.write(f'        "name": "{self._config.variableName(variable_id)}",\n')
                out_file.write(f'        "id": {variable_id},\n')
                variable_type: str = self._config.variableType(variable_id)
                out_file.write(f'        "type": "{variable_type}",\n')
                enabled_string: str = "true" if self._config.variableIsEnabled(variable_id) else "false"
                out_file.write(f'        "enabled": {enabled_string},\n')

                match variable_type:
                    case 'radio':
                        Package._writeBooleanEntryFromValue(out_file, 'persist', self._config.variableIsPersistent(variable_id))
                        Package._writeBooleanEntryFromValue(out_file, 'writeonly', self._config.variableIsWriteOnly(variable_id))
                        Package._writeStringEntryFromValue(out_file, 'group', self._config.variableGroup(variable_id))
                        out_file.write(f'        "defaultval": {1 if self._config.variableBooleanDefault(variable_id) else 0},\n')
                        Package._writeStringEntryFromValue(out_file, 'value', self._config.variableValueOn(variable_id))
                        Package._writeStringEntryFromValue(out_file, 'value_off', self._config.variableValueOff(variable_id))
                        Package._writeStringEntryFromValue(out_file, 'mask', self._config.variableMask(variable_id))
                    case 'check':
                        Package._writeBooleanEntryFromValue(out_file, 'persist', self._config.variableIsPersistent(variable_id))
                        Package._writeBooleanEntryFromValue(out_file, 'writeonly', self._config.variableIsWriteOnly(variable_id))
                        out_file.write(f'        "defaultval": {1 if self._config.variableBooleanDefault(variable_id) else 0},\n')
                        Package._writeStringEntryFromValue(out_file, 'value', self._config.variableValueOn(variable_id))
                        Package._writeStringEntryFromValue(out_file, 'value_off', self._config.variableValueOff(variable_id))
                        Package._writeStringEntryFromValue(out_file, 'mask', self._config.variableMask(variable_id))
                    case 'slider_u32':
                        Package._writeBooleanEntryFromValue(out_file, 'persist', self._config.variableIsPersistent(variable_id))
                        Package._writeBooleanEntryFromValue(out_file, 'writeonly', self._config.variableIsWriteOnly(variable_id))
                        Package._writeStringEntryFromValue(out_file, 'defaultval', self._config.variableDefaultValue(variable_id))
                        Package._writeStringEntryFromValue(out_file, 'mask', self._config.variableMask(variable_id))

                        out_file.write('          "graphical": {\n')
                        Package._writeBooleanEntryFromValue(out_file, 'signed', self._config.variableValueIsSigned(variable_id), extra_spaces='  ')
                        Package._writeStringEntryFromValue(out_file, 'min', self._config.variableMinimumValue(variable_id), extra_spaces='  ')
                        Package._writeStringEntryFromValue(out_file, 'max', self._config.variableMaximumValue(variable_id), extra_spaces='  ')
                        Package._writeStringEntryFromValue(out_file, 'adjust_small', self._config.variableSmallStep(variable_id), extra_spaces='  ')
                        Package._writeStringEntryFromValue(out_file, 'adjust_large', self._config.variableLargeStep(variable_id), extra_spaces='  ')
                        out_file.write('          }\n')
                    case 'list':
                        Package._writeBooleanEntryFromValue(out_file, 'persist', self._config.variableIsPersistent(variable_id))
                        Package._writeBooleanEntryFromValue(out_file, 'writeonly', self._config.variableIsWriteOnly(variable_id))
                        Package._writeStringEntryFromValue(out_file, 'defaultval', self._config.variableDefaultValue(variable_id))

                        found_an_option: bool = False

                        out_file.write('        "options": [')
                        for option in self._config.variableOptions(variable_id):
                            if found_an_option is True:
                                out_file.write(',')

                            out_file.write('\n          {\n')
                            Package._writeStringEntryFromValue(out_file, 'value', option[1], extra_spaces='    ')
                            out_file.write('            "name": "{option[0]}"\n')
                            out_file.write('          }')

                            found_an_option = True

                        out_file.write('\n        ]\n')
                    case 'action':
                        Package._writeStringEntryFromValue(out_file, 'value', self._config.variableValue(variable_id))
                        Package._writeStringEntryFromValue(out_file, 'mask', self._config.variableMask(variable_id))

                address: str = self._config.variableAddress(variable_id)
                address_string: str = f'"{address}"' if address.startswith('0x') else address
                out_file.write(f'        "address": {address_string}\n')
                out_file.write('      }')

                found_a_variable = True

            if found_a_variable:
                out_file.write('\n    ')

            out_file.write('],\n')
            out_file.write('    "messages": []\n')
            out_file.write('  }\n')
            out_file.write('}\n')

    def _generateCoreFile(self) -> None:
        with open(os.path.join(self._cores_folder, 'core.json'), 'w') as out_file:
            out_file.write('{\n')
            out_file.write('  "core": {\n')
            out_file.write('    "magic": "APF_VER_1",\n')
            out_file.write('    "metadata": {\n')
            out_file.write('      "platform_ids": ["%s"],\n' % (self._config.platformShortName()))
            out_file.write('      "shortname": "%s",\n' % (self._config.platformShortName()))
            out_file.write('      "description": "%s",\n' % (self._config.platformDescription()))
            out_file.write('      "author": "%s",\n' % (self._config.authorName()))
            out_file.write('      "url": "%s",\n' % (self._config.authorURL()))
            out_file.write('      "version": "%s",\n' % (self._config.buildVersion()))
            out_file.write('      "date_release": "%s"\n' % (self._today))
            out_file.write('    },\n')
            out_file.write('    "framework": {\n')
            out_file.write('      "target_product": "Analogue Pocket",\n')
            out_file.write('      "version_required": "1.1",\n')
            out_file.write('      "sleep_supported": false,\n')
            out_file.write('      "dock": {\n')
            out_file.write('        "supported": true,\n')
            out_file.write('        "analog_output": false\n')
            out_file.write('      },\n')
            out_file.write('      "hardware": {\n')
            out_file.write('        "link_port": false,\n')
            out_file.write('        "cartridge_adapter": %d\n' % (0 if self._config.powerCartridgePort() else -1))
            out_file.write('      }\n')
            out_file.write('    },\n')

            found_a_core: bool = False
            out_file.write('    "cores": [')
            for core_id in self._config.coresList():
                if found_a_core is True:
                    out_file.write(',')

                out_file.write('\n      {\n')

                core_name = self._config.coreName(core_id)
                if core_name is not None:
                    out_file.write(f'        "name": "{core_name}",\n')

                out_file.write(f'        "id": {core_id},\n')
                out_file.write(f'        "filename": "{self._config.coreFilename(core_id)}"\n')
                out_file.write('      }')

                found_a_core = True

            if found_a_core:
                out_file.write('\n    ')

            out_file.write(']\n')
            out_file.write('  }\n')
            out_file.write('}\n')

    def _generateInputFile(self) -> None:
        with open(os.path.join(self._cores_folder, 'input.json'), 'w') as out_file:
            out_file.write('{\n')
            out_file.write('  "input": {\n')
            out_file.write('    "magic": "APF_VER_1",\n')
            out_file.write('    "controllers": [')

            found_a_controller: bool = False
            for controller_id in self._config.controllerList():
                if found_a_controller is True:
                    out_file.write(',')

                out_file.write('\n      {\n')

                out_file.write('        "type": "default",\n')
                out_file.write('        "mappings": [')

                mapping_id: int = 0
                for mapping in self._config.controllerKeyMapping(controller_id):
                    if mapping_id != 0:
                        out_file.write(',')

                    out_file.write('\n          {\n')
                    out_file.write(f'            "id": {mapping_id},\n')
                    out_file.write(f'            "name": "{mapping[0]}",\n')
                    out_file.write(f'            "key": "{mapping[1]}"\n')
                    out_file.write('          }')

                    mapping_id += 1

                out_file.write('\n        ]\n')
                out_file.write('      }')

                found_a_controller = True

            if found_a_controller:
                out_file.write('\n    ')

            out_file.write(']\n')
            out_file.write('  }\n')
            out_file.write('}\n')

    def _generateDefinitionFiles(self) -> None:
        output_filename = os.path.join(self._cores_folder, 'audio.json')
        with open(output_filename, 'w') as out_file:
            out_file.write('{\n')
            out_file.write('  "audio": {\n')
            out_file.write('    "magic": "APF_VER_1"\n')
            out_file.write('  }\n')
            out_file.write('}\n')

        self._generateDataFile()
        self._generateInputFile()

        output_filename = os.path.join(self._cores_folder, 'variants.json')
        with open(output_filename, 'w') as out_file:
            out_file.write('{\n')
            out_file.write('  "variants": {\n')
            out_file.write('    "magic": "APF_VER_1",\n')
            out_file.write('    "variant_list": []\n')
            out_file.write('  }\n')
            out_file.write('}\n')

        self._generateInteractFile()

        output_filename = os.path.join(self._cores_folder, 'video.json')
        with open(output_filename, 'w') as out_file:
            out_file.write('{\n')
            out_file.write('  "video": {\n')
            out_file.write('    "magic": "APF_VER_1",\n')
            out_file.write('    "scaler_modes": [\n')
            out_file.write('      {\n')
            out_file.write('        "width": %d,\n' % (self._config.videoWidth()))
            out_file.write('        "height": %d,\n' % (self._config.videoHeight()))
            out_file.write('        "aspect_w": %d,\n' % (self._config.videoAspectRatioWidth()))
            out_file.write('        "aspect_h": %d,\n' % (self._config.videoAspectRatioHeight()))
            out_file.write('        "rotation": %d,\n' % (self._config.videoRotationAngle()))

            flip_video: int = 0
            if self._config.videoFlipHorizontal():
                flip_video |= 2
            if self._config.videoFlipVertical():
                flip_video |= 1

            out_file.write('        "mirror": %d\n' % (flip_video))
            out_file.write('      }\n')
            out_file.write('    ]\n')
            out_file.write('  }\n')
            out_file.write('}\n')

        output_filename = os.path.join(self._platforms_folder, '%s.json' % (self._config.platformShortName()))
        with open(output_filename, 'w') as out_file:
            out_file.write('{\n')
            out_file.write('  "platform": {\n')
            out_file.write('    "category": "%s",\n' % (self._config.platformCategory()))
            out_file.write('    "name": "%s",\n' % (self._config.platformName()))
            out_file.write('    "year": %s,\n' % (self._today.split('-')[0]))
            out_file.write('    "manufacturer": "%s"\n' % (self._config.authorName()))
            out_file.write('  }\n')
            out_file.write('}\n')

        self._generateCoreFile()

    def _addImages(self) -> None:
        src_image: str = self._config.platformImage()
        dest_bin_file = os.path.join(self._platforms_images_folder, '%s.bin' % (self._config.platformShortName()))

        if src_image.endswith('.bin'):
            shutil.copyfile(src_image, dest_bin_file)
        else:
            pfDevTools.Convert([src_image, dest_bin_file], debug_on=self._debug_on).run()

        src_image = self._config.authorIcon()
        dest_bin_file = os.path.join(self._cores_folder, 'icon.bin')

        if src_image.endswith('.bin'):
            shutil.copyfile(src_image, dest_bin_file)
        else:
            pfDevTools.Convert([src_image, dest_bin_file], debug_on=self._debug_on).run()

    def _packageCore(self):
        packaged_filename = os.path.abspath(os.path.join(self._destination_folder, self.packagedFilename()))
        if os.path.exists(packaged_filename):
            os.remove(packaged_filename)

        with zipfile.ZipFile(packaged_filename, 'w') as myzip:
            for p in Path(self._packaging_folder).rglob('*'):
                if os.path.isdir(p):
                    continue

                relative_path = p.relative_to(self._packaging_folder)
                print('   adding \'' + str(relative_path) + '\'')
                myzip.write(p, arcname=relative_path, compress_type=zipfile.ZIP_DEFLATED)

    def dependencies(self) -> List[str]:
        deps: List[str] = [self._config.config_filename,
                           self._config.platformImage(),
                           self._config.authorIcon()]

        for file in self._bitstream_files:
            # -- First entry is the source bitstream file.
            deps.append(file[0])

        info_file = self._config.platformInfoFile()
        if info_file is not None:
            deps.append(info_file)

        return deps

    def packagedFilename(self) -> str:
        return '%s-%s-%s.zip' % (self._config.fullPlatformName(), self._config.buildVersion(), self._today)

    def run(self) -> None:
        try:
            # -- We delete the core packaging folder in case stale files are in there (for example after changing the core config file)
            if os.path.exists(self._packaging_folder):
                shutil.rmtree(self._packaging_folder)

            os.makedirs(self._packaging_folder)
            os.makedirs(self._cores_folder, exist_ok=True)
            os.makedirs(self._platforms_folder, exist_ok=True)
            os.makedirs(self._platforms_images_folder, exist_ok=True)

            print('Reversing bitstream files...')
            for file in self._bitstream_files:
                pfDevTools.Reverse([file[0], os.path.join(self._cores_folder, file[1])], debug_on=self._debug_on).run()

            print('Generating definitions files...')
            self._generateDefinitionFiles()

            print('Adding images...')
            self._addImages()

            info_file = self._config.platformInfoFile()
            if info_file is not None:
                dest_info = os.path.join(self._cores_folder, 'info.txt')
                shutil.copyfile(info_file, dest_info)

            print('Packaging core...')
            self._packageCore()
        except Exception as e:
            if self._debug_on:
                print(traceback.format_exc())
            elif len(str(e)) != 0:
                print(f'ERROR: {e}')
            else:
                print('ERROR: Unknown error while packaging core.')

            sys.exit(1)
