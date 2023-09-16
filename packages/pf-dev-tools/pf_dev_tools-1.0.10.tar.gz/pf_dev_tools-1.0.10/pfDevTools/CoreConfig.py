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

from typing import Dict
from typing import List
from sys import platform
from enum import IntFlag

from .Exceptions import ArgumentError

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib


# -- Constants
class FileParameter(IntFlag):
    USER_RELOADABLE = 0x0001
    CORE_SPECIFIC = 0x0002
    NON_VOLATILE_FILENAME = 0x0004
    READ_ONLY = 0x0008
    INSTANCE_JSON = 0x0010
    INIT_NON_VOLATILE_DATA_ON_LOAD = 0x0020
    RESET_CORE_WHILE_LOADING = 0x0040
    RESTART_CORE_AFTER_LOADING = 0x0080
    FULL_RELOAD_CORE = 0x0100
    PERSIST_BROWSED_FILENAME = 0x0200


# -- Classes
class CoreConfig:
    """A class for openFPGA core configurations"""

    @classmethod
    def coreInstallVolumePath(cls) -> str:
        # -- On macOS, if PF_CORE_INSTALL_VOLUME is not defined, we default to POCKET
        volume_name: str = os.environ.get('PF_CORE_INSTALL_VOLUME', "POCKET")
        if platform == "darwin":
            return os.path.join('/Volumes', volume_name)
        else:
            raise RuntimeError('PF_CORE_INSTALL_VOLUME is not defined in the environment.')

    @classmethod
    def _numericValueToString(cls, value, default_value=None, signed_allowed: bool = False):
        if value is None:
            return default_value

        if isinstance(value, str):
            if not value.startswith('0x') or len(value) > 10:
                return None

            try:
                int(value[2:], 16)
            except Exception:
                return None

            return value
        else:
            if signed_allowed:
                if value > 2147483647 or value < -2147483648:
                    return None
            elif value < 0:
                raise None

            if value > 0xFFFFFFFF:
                return None

            return f"{value}"

    @classmethod
    def coreSectionName(cls, core_id: str) -> str:
        return f'Cores.{core_id}'

    @classmethod
    def fileSlotSectionName(cls, slot_id: str) -> str:
        return f'Files.{slot_id}'

    @classmethod
    def variableSectionName(cls, variable_id: str) -> str:
        return f'Variables.{variable_id}'

    @classmethod
    def controllerSectionName(cls, controller_id: str) -> str:
        return f'Controllers.{controller_id}'

    def __init__(self, config_filename: str):
        """Constructor based on config file path."""

        self.config_filename: str = config_filename
        self._platform_short_name = None

        components = os.path.splitext(self.config_filename)
        if len(components) != 2 or components[1] != '.toml':
            raise ArgumentError('Config file needs to be a toml file.')

        if not os.path.exists(self.config_filename):
            raise ArgumentError('Config file \'' + self.config_filename + '\' does not exist.')

        self.config_file_folder = os.path.dirname(self.config_filename)

        with open(self.config_filename, mode="rb") as fp:
            self._config = tomllib.load(fp)

        # -- If no cores are specified, we default to this single one.
        if self._config.get('Cores', None) is None:
            self._config['Cores'] = {'0': {'name': 'default',
                                           'source_file': 'pf_core.rbf',
                                           'filename': 'bitstream.rbf_r'}}

    def _getConfigCategory(self, category_name: str) -> Dict:
        return self._config.get(category_name, {})

    def _getConfigParam(self, section_name: str, param_name: str, optional=False):
        section: Dict = None

        section_name_parts = section_name.split('.')
        number_of_parts = len(section_name_parts)
        if number_of_parts > 1:
            if number_of_parts > 2:
                raise ArgumentError(f'Invalid section named {section_name} is being searched config file.')

            from_config: Dict = self._config.get(section_name_parts[0])
            section = from_config.get(section_name_parts[1], None)
        else:
            section = self._config.get(section_name, None)

        if section is None:
            if optional is False:
                raise ArgumentError(f'Can\'t find section named {section_name} in config file.')
            else:
                return None

        param = section.get(param_name, None)
        if param is None:
            if optional is False:
                raise ArgumentError(f'Can\'t find parameter {param_name} in section {section_name} in config file.')
            else:
                return None

        return param

    def _readBooleanFromConfigParam(self, section_name: str, param_name: str, optional=False) -> bool:
        value: bool = self._getConfigParam(section_name, param_name, optional=optional)
        if value is not None and not isinstance(value, bool):
            raise ArgumentError(f'Found invalid value \'{value}\' for \'{param_name}\' in \'{section_name}\'. Should be a boolean.')

        return value

    def _readBooleanFromFileParam(self, slot_id: str, param_name: str, optional=False) -> bool:
        return self._readBooleanFromConfigParam(CoreConfig.fileSlotSectionName(slot_id), param_name, optional=optional)

    def _readBooleanFromVariableParam(self, variable_id: str, param_name: str, optional=False) -> bool:
        return self._readBooleanFromConfigParam(CoreConfig.variableSectionName(variable_id), param_name, optional=optional)

    def platformName(self) -> str:
        return self._getConfigParam('Platform', 'name')

    def platformImage(self) -> str:
        return os.path.join(self.config_file_folder, self._getConfigParam('Platform', 'image'))

    def platformShortName(self) -> str:
        if self._platform_short_name is None:
            self._platform_short_name = self._getConfigParam('Platform', 'short_name')

            if len(self._platform_short_name) > 31:
                raise ArgumentError(f'Invalid platform short name \'{self._platform_short_name}\'. Maximum length is 31 characters.')

            for c in self._platform_short_name:
                if (c.isalnum() is False) or c.isupper():
                    raise ArgumentError(f'Invalid platform short name \'{self._platform_short_name}\'. Should be lower-case and can only contain a-z, 0-9 or _.')

        return self._platform_short_name

    def platformCoreFilename(self) -> str:
        filename: str = f'{self._config.platformCoreFilename()}.rbf_r'
        if len(filename) > 15:
            raise ArgumentError(f'Invalid platform core filename \'{filename}\'. Maximum length is 15 characters.')

        return filename

    def platformCategory(self) -> str:
        return self._getConfigParam('Platform', 'category')

    def platformDescription(self) -> str:
        value = self._getConfigParam('Platform', 'description')
        if len(value) > 63:
            raise ArgumentError(f'Invalid platform description \'{value}\'. Maximum length is 63 characters.')

        return value

    def platformInfoFile(self) -> str:
        platform_config = self._config.get('Platform', None)
        if platform_config is not None:
            info_file = platform_config.get('info', None)

            if info_file is not None:
                return os.path.expandvars(os.path.join(self.config_file_folder, info_file))

        return None

    def coresList(self) -> List[str]:
        list = self._getConfigCategory('Cores').keys()
        if len(list) == 0:
            raise ArgumentError('Did not find any cores to build in the config file.')
        if len(list) > 8:
            raise ArgumentError('Found more than 8 cores in the config file.')

        for core_id in list:
            if int(core_id) > 0xFFFF:
                raise ArgumentError(f'Found invalid core id \'{CoreConfig.coreSectionName(core_id)}\'. ID should fit in a 16-bit unsigned.')

        return list

    def coreName(self, core_id: str) -> str:
        core_section_name: str = CoreConfig.coreSectionName(core_id)
        core_name: str = self._getConfigParam(core_section_name, 'name', optional=True)
        if core_name is not None and len(core_name) > 15:
            raise ArgumentError(f'Found invalid core name for \'{core_section_name}\'. Maximum length is 15 characters.')

        return core_name

    def coreFilename(self, core_id: str) -> str:
        core_section_name: str = CoreConfig.coreSectionName(core_id)
        filename: str = self._getConfigParam(core_section_name, 'filename')
        if len(filename) > 15:
            raise ArgumentError(f'Found invalid core filename for \'{core_section_name}\'. Maximum length is 15 characters.')

        return filename

    def coreSourceFile(self, core_id: str) -> str:
        return self._getConfigParam(CoreConfig.coreSectionName(core_id), 'source_file')

    def buildVersion(self) -> str:
        value = self._getConfigParam('Build', 'version')
        if len(value) > 31:
            raise ArgumentError(f'Invalid platform version \'{value}\'. Maximum length is 31 characters.')

        return value

    def authorName(self) -> str:
        value = self._getConfigParam('Author', 'name')
        if len(value) > 31:
            raise ArgumentError(f'Invalid platform author \'{value}\'. Maximum length is 31 characters.')

        return value

    def authorIcon(self) -> str:
        return os.path.join(self.config_file_folder, self._getConfigParam('Author', 'icon'))

    def authorURL(self) -> str:
        value = self._getConfigParam('Author', 'url')
        if len(value) > 63:
            raise ArgumentError(f'Invalid platform URL \'{value}\'. Maximum length is 63 characters.')

        return value

    def videoWidth(self) -> str:
        return self._getConfigParam('Hardware', 'video_width')

    def videoHeight(self) -> str:
        return self._getConfigParam('Hardware', 'video_height')

    def videoAspectRatioWidth(self) -> str:
        return self._getConfigParam('Hardware', 'video_aspect_w')

    def videoAspectRatioHeight(self) -> str:
        return self._getConfigParam('Hardware', 'video_aspect_h')

    def videoRotationAngle(self) -> int:
        value = self._getConfigParam('Hardware', 'video_rotation_angle', optional=True)
        if value is None:
            value = 0
        elif not isinstance(value, int) or (value != 0 and value != 90 and value != 180 and value != 270):
            raise ArgumentError(f'Invalid platform video_rotation_angle \'{value}\'. Should be 0, 90, 180 or 270.')

        return value

    def videoFlipHorizontal(self) -> bool:
        value = self._readBooleanFromConfigParam('Hardware', 'video_flip_horizontal', optional=True)
        return value if value is not None else False

    def videoFlipVertical(self) -> bool:
        value = self._readBooleanFromConfigParam('Hardware', 'video_flip_vertical', optional=True)
        return value if value is not None else False

    def powerCartridgePort(self) -> bool:
        power_port: bool = self._readBooleanFromConfigParam('Hardware', 'power_cartridge_port', optional=True)
        return power_port if power_port is not None else False

    def fullPlatformName(self) -> str:
        return f'{self.authorName()}.{self.platformShortName()}'

    def fileSlotList(self) -> List[str]:
        list = self._getConfigCategory('Files').keys()
        if len(list) > 32:
            raise ArgumentError('Found more than 32 file slots in the config file.')

        for slot_id in list:
            if int(slot_id) > 0xFFFF:
                raise ArgumentError(f'Found invalid file slot id \'{CoreConfig.fileSlotSectionName(slot_id)}\'. Must be a 16-bit unsigned integer.')

        return list

    def fileSlotName(self, slot_id: str) -> str:
        file_section_name: str = CoreConfig.fileSlotSectionName(slot_id)
        slot_name: str = self._getConfigParam(file_section_name, 'name')
        if len(slot_name) > 15:
            raise ArgumentError(f'Found invalid slot name for \'{file_section_name}\'. Maximum length is 15 characters.')

        return slot_name

    def fileSlotRequired(self, slot_id: str) -> bool:
        return self._readBooleanFromFileParam(slot_id, 'required')

    def fileSlotDeferLoad(self, slot_id: str) -> bool:
        return self._readBooleanFromFileParam(slot_id, 'deferload', optional=True)

    def fileSlotSecondary(self, slot_id: str) -> bool:
        return self._readBooleanFromFileParam(slot_id, 'secondary', optional=True)

    def fileSlotNonVolatile(self, slot_id: str) -> bool:
        return self._readBooleanFromFileParam(slot_id, 'non-volatile', optional=True)

    def fileSlotFilename(self, slot_id: str) -> str:
        file_section_name: str = CoreConfig.fileSlotSectionName(slot_id)
        filename: str = self._getConfigParam(file_section_name, 'filename')
        if filename is not None:
            if len(filename) > 31:
                raise ArgumentError(f'Found invalid filename for \'{file_section_name}\'. Maximum length is 31 characters.')

        return filename

    def fileSlotParameters(self, slot_id: str) -> int:
        values: Dict[str, int] = {
            'user-reloadable': FileParameter.USER_RELOADABLE,
            'core-specific': FileParameter.CORE_SPECIFIC,
            'nonvolatile-filename': FileParameter.NON_VOLATILE_FILENAME,
            'read-only': FileParameter.READ_ONLY,
            'instance-json': FileParameter.INSTANCE_JSON,
            'init-nonvolatile-data-on-load': FileParameter.INIT_NON_VOLATILE_DATA_ON_LOAD,
            'reset-core-while-loading': FileParameter.RESET_CORE_WHILE_LOADING,
            'restart-core-after-loading': FileParameter.RESTART_CORE_AFTER_LOADING,
            'full-reload-core': FileParameter.FULL_RELOAD_CORE,
            'persist-browsed-filename': FileParameter.PERSIST_BROWSED_FILENAME
        }

        parameters: int = 0

        file_section_name: str = CoreConfig.fileSlotSectionName(slot_id)
        params = self._getConfigParam(file_section_name, 'parameters', optional=True)
        for param in params if params is not None else []:
            bit_value: FileParameter = values.get(param, None)

            if bit_value is None:
                raise ArgumentError(f'Unknown data slot parameter \'{param}\' for file slot \'{file_section_name}\'.')

            parameters |= bit_value

        return parameters

    def fileSlotExtensions(self, slot_id: str) -> List[str]:
        file_section_name: str = CoreConfig.fileSlotSectionName(slot_id)
        extensions: List[str] = self._getConfigParam(file_section_name, 'extensions', optional=True)
        if extensions is None:
            extensions = []
        elif len(extensions) > 4:
            raise ArgumentError(f'Too many extensions for file slot \'{file_section_name}\'. Limit is 4.')

        return extensions

    def fileSlotRequiredSize(self, slot_id: str) -> str:
        file_section_name: str = CoreConfig.fileSlotSectionName(slot_id)
        size = self._getConfigParam(file_section_name, 'required_size', optional=True)
        if size is not None:
            size = CoreConfig._numericValueToString(size)
            if size is None:
                raise ArgumentError(f'Invalid required size for \'{file_section_name}\'. Required size is 32-bit unsigned integer or hex string with 0x prefix.')

        return size

    def fileSlotMaximumSize(self, slot_id: str) -> str:
        file_section_name: str = CoreConfig.fileSlotSectionName(slot_id)
        size = self._getConfigParam(file_section_name, 'maximum_size', optional=True)
        if size is not None:
            size = CoreConfig._numericValueToString(size)

            if size is None:
                raise ArgumentError(f'Invalid maximum size for \'{file_section_name}\'. Maximum size is 32-bit unsigned integer or hex string with 0x prefix.')

        return size

    def fileSlotAddress(self, slot_id: str) -> str:
        file_section_name: str = CoreConfig.fileSlotSectionName(slot_id)
        address = CoreConfig._numericValueToString(self._getConfigParam(file_section_name, 'address'))
        if address is None:
            raise ArgumentError(f'Invalid address for \'{file_section_name}\'. Maximum size is 32-bit unsigned integer or hex string with 0x prefix.')

        return address

    def variableList(self) -> List[str]:
        list = self._getConfigCategory('Variables').keys()
        if len(list) > 16:
            raise ArgumentError('Found more than 16 variables in the config file.')

        for variable_id in list:
            if int(variable_id) > 0xFFFF:
                raise ArgumentError(f'Found invalid variable id \'{CoreConfig.variableSectionName(variable_id)}\'. Must be a 16-bit unsigned integer.')

        return list

    def variableName(self, variable_id: str) -> str:
        variable_section_name: str = CoreConfig.variableSectionName(variable_id)
        variable_name: str = self._getConfigParam(variable_section_name, 'name')
        if len(variable_name) > 23:
            raise ArgumentError(f'Found invalid variable name for \'{variable_section_name}\'. Maximum length is 23 characters.')

        return variable_name

    def variableType(self, variable_id: str) -> str:
        values: Dict[str, int] = {
            'radio': 'radio',
            'check': 'check',
            'slider': 'slider_u32',
            'list': 'list',
            'number': 'number_u32',
            'action': 'action'
        }

        variable_section_name: str = CoreConfig.variableSectionName(variable_id)
        variable_type: str = self._getConfigParam(variable_section_name, 'type')
        json_variable_type: str = values.get(variable_type, None)
        if json_variable_type is None:
            raise ArgumentError(f'Found invalid variable type \'{variable_type}\' for \'{variable_section_name}\'.')

        return json_variable_type

    def variableIsEnabled(self, variable_id: str) -> bool:
        return self._readBooleanFromVariableParam(variable_id, 'enabled')

    def variableAddress(self, variable_id: str) -> str:
        variable_section_name: str = CoreConfig.variableSectionName(variable_id)
        address = CoreConfig._numericValueToString(self._getConfigParam(variable_section_name, 'address'))
        if address is None:
            raise ArgumentError(f'Invalid \'address\' for \'{variable_section_name}\'. Must be a 32-bit unsigned integer or hex string.')

        return address

    def variableIsPersistent(self, variable_id: str) -> bool:
        return self._readBooleanFromVariableParam(variable_id, 'persistent', optional=True)

    def variableIsWriteOnly(self, variable_id: str) -> bool:
        return self._readBooleanFromVariableParam(variable_id, 'write-only', optional=True)

    def variableBooleanDefault(self, variable_id: str) -> bool:
        value: bool = self._readBooleanFromVariableParam(variable_id, 'default')
        if value is None:
            raise ArgumentError(f'Invalid or missing \'default\' for \'{CoreConfig.variableSectionName(variable_id)}\'.')

        return value

    def variableIntOrHexStringValue(self, variable_id: str, value_name: str, optional: bool = False, signed_allowed: bool = False):
        variable_section_name: str = CoreConfig.variableSectionName(variable_id)
        value = self._getConfigParam(variable_section_name, value_name, optional=optional)
        if value is not None:
            value = CoreConfig._numericValueToString(value, signed_allowed)
            if value is None:
                sign_string = 'signed' if signed_allowed else 'unsigned'
                raise ArgumentError(f'Invalid \'{value_name}\' for \'{variable_section_name}\'. Must be a 32-bit {sign_string} integer or hex string.')

        return value

    def variableGroup(self, variable_id: str):
        return self.variableIntOrHexStringValue(variable_id, 'group')

    def variableValueOn(self, variable_id: str):
        return self.variableIntOrHexStringValue(variable_id, 'value_on')

    def variableValueOff(self, variable_id: str):
        return self.variableIntOrHexStringValue(variable_id, 'value_off', optional=True)

    def variableMask(self, variable_id: str):
        return self.variableIntOrHexStringValue(variable_id, 'mask', optional=True)

    def variableDefaultValue(self, variable_id: str):
        return self.variableIntOrHexStringValue(variable_id, 'default_value')

    def variableValue(self, variable_id: str):
        return self.variableIntOrHexStringValue(variable_id, 'value')

    def variableValueIsSigned(self, variable_id: str):
        return self._readBooleanFromVariableParam(variable_id, 'signed_value', optional=True)

    def variableMinimumValue(self, variable_id: str):
        return self.variableIntOrHexStringValue(variable_id, 'minimum_value', signed_allowed=True if self.variableValueIsSigned(variable_id) is True else False)

    def variableMaximumValue(self, variable_id: str):
        return self.variableIntOrHexStringValue(variable_id, 'maximum_value', signed_allowed=True if self.variableValueIsSigned(variable_id) is True else False)

    def variableSmallStep(self, variable_id: str):
        return self.variableIntOrHexStringValue(variable_id, 'small_step', signed_allowed=True if self.variableValueIsSigned(variable_id) is True else False)

    def variableLargeStep(self, variable_id: str):
        return self.variableIntOrHexStringValue(variable_id, 'large_step', signed_allowed=True if self.variableValueIsSigned(variable_id) is True else False)

    def variableOptions(self, variable_id: str):
        variable_section_name: str = CoreConfig.variableSectionName(variable_id)
        options = self._getConfigParam(variable_section_name, 'choices')
        if len(options) > 16:
            raise ArgumentError(f'Too many options for variable \'{variable_section_name}\'. Maximum supported is 16.')

        results = []
        for option in options:
            if len(option) != 2:
                raise ArgumentError(f'Invalid option for variable \'{variable_section_name}\'. Format is [ <name>, <value> ].')

            name: str = option[0]
            if len(name) > 23:
                raise ArgumentError(f'Invalid option name \'{name}\' for variable \'{variable_section_name}\'. Maximum length is 23 characters.')

            value_as_string = CoreConfig._numericValueToString(option[1])
            if value_as_string is None:
                raise ArgumentError(f'Invalid option value \'{option[1]}\' for variable \'{variable_section_name}\'. Must be a 32-bit unsigned integer or hex string.')

            results.append([name, value_as_string])

        return results

    def controllerList(self) -> List[str]:
        list = self._getConfigCategory('Controllers').keys()
        if len(list) > 4:
            raise ArgumentError('Found more than 4 controllers in the config file.')

        for controller_id in list:
            id_as_int: int = int(controller_id)
            if id_as_int < 1 or id_as_int > 4:
                raise ArgumentError(f'Found invalid controller id \'{CoreConfig.controllerSectionName(controller_id)}\'. ID should be between 1 and 4.')

        return list

    def controllerKeyMapping(self, controller_id: str) -> List[List[str]]:
        values: Dict[str, int] = {
            'A': 'pad_btn_a',
            'B': 'pad_btn_b',
            'X': 'pad_btn_x',
            'Y button': 'pad_btn_y',
            'L': 'pad_trig_l',
            'R': 'pad_trig_r',
            'Start': 'pad_btn_start',
            'Select': 'pad_btn_select',
        }

        controller_section_name: str = CoreConfig.controllerSectionName(controller_id)
        mappings = self._getConfigParam(controller_section_name, 'key_mapping')

        if len(mappings) > 8:
            raise ArgumentError(f'Found too many mappings for controller id \'{controller_section_name}\'. Maximum allowed is 8.')

        results = []
        for mapping in mappings:
            if len(mapping) != 2:
                raise ArgumentError(f'Invalid mapping for controller \'{controller_section_name}\'. Format is [ <name>, <button> ].')

            name: str = mapping[0]
            if len(name) > 19:
                raise ArgumentError(f'Invalid mapping name \'{name}\' for controller \'{controller_section_name}\'. Maximum length is 20 characters.')

            button = values.get(mapping[1], None)
            if button is None:
                raise ArgumentError(f'Invalid button name \'{mapping[1]}\' for controller \'{controller_section_name}\'.')

            results.append([name, button])

        return results
