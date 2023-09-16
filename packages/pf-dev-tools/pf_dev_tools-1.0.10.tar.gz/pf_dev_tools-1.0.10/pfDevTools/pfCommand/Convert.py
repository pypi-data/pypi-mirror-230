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

from PIL import Image


# -- Classes
class Convert:
    """A tool to install a zipped up core file onto a given volume (SD card or Pocket in USB access mode)."""

    def __init__(self, arguments, debug_on: bool = False):
        """Constructor based on command line arguments."""

        self._debug_on: bool = debug_on

        # -- Gather the arguments
        nb_of_arguments: int = len(arguments)
        if nb_of_arguments != 2:
            raise RuntimeError('Invalid arguments. Maybe start with `pf --help?')

        self._img_filename: str = arguments[0]
        self._bin_filename: str = arguments[1]

        if not os.path.exists(self._img_filename):
            raise RuntimeError('File \'' + self._img_filename + '\' does not exist.')

    def run(self) -> None:
        try:
            print('Reading \'' + self._img_filename + '\'.')
            img = Image.open(self._img_filename).convert("RGB")

            pixels = img.load()

            byte_data = []
            warned_against_greyscale = False

            # -- Analog Pocket Image Format is 16-bit monochrome stored rotated 90 degrees counter-clockwise.
            for x in range(img.width - 1, -1, -1):
                for y in range(0, img.height):
                    pixel = pixels[x, y]
                    if warned_against_greyscale is False and ((pixel[0] != pixel[1]) or (pixel[0] != pixel[2])):
                        print('WARNING: Image is not greyscale, results may be incorrect.')
                        warned_against_greyscale = True

                    # -- Each pixel is 16 bits. The brightness is stored in the upper 8 bits.
                    # -- A fully on pixel value is 0xFF00. A fully off pixel value is 0x0000.
                    # -- Source image should be greyscale but in case it isn't, we average RBB here to convert it.
                    byte_data.append(int((pixel[0] + pixel[1] + pixel[2]) / 3))
                    byte_data.append(0x00)

            print('Writing \'' + self._bin_filename + '\'.')
            output_file = open(self._bin_filename, 'wb')
            output_file.write(bytearray(byte_data))
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
        return 'convert'

    @classmethod
    def usage(cls) -> None:
        print('   convert src_filename dest_filename    - Convert an image to the openFGPA binary format.')
