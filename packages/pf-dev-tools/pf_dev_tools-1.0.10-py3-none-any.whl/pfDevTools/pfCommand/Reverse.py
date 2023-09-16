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
import traceback


# -- Classes
class Reverse:
    """A tool to reverse the bitstream of an rbf file for an Analog Pocket core."""

    def __init__(self, arguments, debug_on: bool = False):
        """Constructor based on command line arguments."""

        self._debug_on: bool = debug_on

        if len(arguments) != 2:
            raise RuntimeError('Invalid arguments. Maybe start with `pf --help?')

        self._rbf_filename: str = arguments[0]
        self._rbf_r_filename: str = arguments[1]

        components = os.path.splitext(self._rbf_filename)
        if len(components) != 2 or components[1] != '.rbf':
            raise RuntimeError('Can only reverse .rbf files.')

        if not os.path.exists(self._rbf_filename):
            raise RuntimeError('File \'' + self._rbf_filename + '\' does not exist.')

    def run(self) -> None:
        try:
            print('Reading \'' + self._rbf_filename + '\'.')
            input_file = open(self._rbf_filename, 'rb')
            input_data = input_file.read()
            input_file.close()

            reversed_data = []
            print('Reversing ' + str(len(input_data)) + ' bytes.')
            for byte in input_data:
                reversed_byte = ((byte & 1) << 7) | ((byte & 2) << 5) | ((byte & 4) << 3) | ((byte & 8) << 1) | ((byte & 16) >> 1) | ((byte & 32) >> 3) | ((byte & 64) >> 5) | ((byte & 128) >> 7)
                reversed_data.append(reversed_byte)

            print('Writing \'' + self._rbf_r_filename + '\'.')
            output_file = open(self._rbf_r_filename, 'wb')
            output_file.write(bytearray(reversed_data))
            output_file.close()
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
        return 'reverse'

    @classmethod
    def usage(cls) -> None:
        print('   reverse src_filename dest_filename    - Reverse a bitstream file.')
