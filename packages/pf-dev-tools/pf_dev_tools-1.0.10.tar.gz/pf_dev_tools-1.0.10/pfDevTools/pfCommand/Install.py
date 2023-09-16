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
import zipfile
import tempfile
import contextlib
import traceback
import pfDevTools.Utils
import pfDevTools.CoreConfig

from sys import platform
from distutils.dir_util import copy_tree


# -- Classes
class Install:
    """A tool to install a zipped up core file onto a given volume (SD card or Pocket in USB access mode)."""

    def __init__(self, arguments, debug_on: bool = False):
        """Constructor based on command line arguments."""

        self._debug_on: bool = debug_on
        self._zip_filename: str = None
        self._volume_path: str = None
        self._no_build: bool = False

        nb_of_arguments = len(arguments)
        if nb_of_arguments == 1 and (arguments[0] == '--no_build'):
            self._no_build = True

            nb_of_arguments -= 1
            arguments = arguments[1:]

        if nb_of_arguments != 0:
            if nb_of_arguments == 2:
                self._volume_path = arguments[1]
                arguments = [arguments[0]]
                nb_of_arguments -= 1
            else:
                self._volume_path = pfDevTools.CoreConfig.coreInstallVolumePath()

            if nb_of_arguments != 1:
                raise RuntimeError('Invalid arguments. Maybe start with `pf --help?')

            self._zip_filename = arguments[0]

            components = os.path.splitext(self._zip_filename)
            if len(components) != 2 or components[1] != '.zip':
                raise RuntimeError('Can only install zipped up core files.')

            if not os.path.exists(self._zip_filename):
                raise RuntimeError('File \'' + self._zip_filename + '\' does not exist.')

            if not os.path.exists(self._volume_path):
                raise RuntimeError(f'Volume {self._volume_path} is not mounted.')

    def _destCoresFolder(self) -> str:
        return os.path.join(self._volume_path, 'Cores')

    def _destPlatformsFolder(self) -> str:
        return os.path.join(self._volume_path, 'Platforms')

    def _deleteFile(self, filepath) -> None:
        with contextlib.suppress(FileNotFoundError):
            os.remove(filepath)

    def run(self) -> None:
        if self._volume_path is None:
            command_line: str = 'scons -Q -s install'

            if self._no_build:
                command_line += ' --skip_build'

            if self._debug_on:
                command_line += ' --debug_on'

            pfDevTools.Utils.shellCommand(command_line)

            return

        try:
            # -- In a temporary folder.
            with tempfile.TemporaryDirectory() as tmp_dir:
                # -- Unzip the file.
                with zipfile.ZipFile(self._zip_filename, 'r') as zip_ref:
                    zip_ref.extractall(tmp_dir)

                # -- Copy core files
                print('Copying core files...')

                core_src_folder = os.path.join(tmp_dir, 'Cores')
                core_dest_folder = self._destCoresFolder()

                if not os.path.isdir(core_src_folder):
                    raise RuntimeError('Cannot find \'' + core_src_folder + '\' in the core release zip file.')

                copy_tree(core_src_folder, core_dest_folder)

                # -- Copy platform files
                print('Copying platforms files...')

                platforms_src_folder = os.path.join(tmp_dir, 'Platforms')
                platforms_dest_folder = self._destPlatformsFolder()

                if not os.path.isdir(platforms_src_folder):
                    raise RuntimeError('Cannot find \'' + platforms_src_folder + '\' in the core release zip file.')

                copy_tree(platforms_src_folder, platforms_dest_folder)
        except Exception as e:
            if self._debug_on:
                print(traceback.format_exc())
            elif len(str(e)) != 0:
                print(f'ERROR: {e}')
            else:
                print('ERROR: Unknown error while cloning repo.')

            sys.exit(1)

    @classmethod
    def name(cls) -> str:
        return 'install'

    @classmethod
    def usage(cls) -> None:
        print('   install <--no_build>                  - Install local project core on volume.')
        print('                                           (without building the core first if --no_build is present).')
        print(f'   install zip_file <{"dest_volume" if platform == "darwin" else "volume_path"}>        - Install core on volume.')
