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
import time
import traceback
import pfDevTools
import pfDevTools.Utils
import pfDevTools.CoreConfig

from sys import platform


# -- Classes
class Eject:
    """A tool to eject given volume (SD card or Pocket in USB access mode)."""

    def __init__(self, arguments, debug_on: bool = False):
        """Constructor based on command line arguments."""

        self._debug_on: bool = debug_on

        nb_of_arguments = len(arguments)
        if nb_of_arguments == 0:
            self._volume_path = pfDevTools.CoreConfig.coreInstallVolumePath()
        elif nb_of_arguments == 1:
            self._volume_path = arguments[0]
        else:
            raise RuntimeError('Invalid arguments. Maybe start with `pf --help?')

    def run(self) -> None:
        try:
            if not os.path.exists(self._volume_path):
                raise RuntimeError(f'Volume {self._volume_path} is not mounted.')

            if platform == "darwin":
                print(f'Ejecting {self._volume_path}.')
                pfDevTools.Utils.shellCommand(f'diskutil eject {self._volume_path}')

                while os.path.exists(self._volume_path):
                    time.sleep(1)

                print('Done.')
            else:
                print('Ejecting volumes is only supported on macOS right now.')
        except Exception as e:
            if self._debug_on:
                print(traceback.format_exc())
            elif len(str(e)) != 0:
                print(f'ERROR: {e}')
            else:
                print('ERROR: Unknown error while ejecting volume.')

            sys.exit(1)

    @classmethod
    def name(cls) -> str:
        return 'eject'

    @classmethod
    def usage(cls) -> None:
        print('   eject <dest_volume>                   - Eject volume.')
