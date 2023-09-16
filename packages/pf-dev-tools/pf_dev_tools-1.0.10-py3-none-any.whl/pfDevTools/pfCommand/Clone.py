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
import pfDevTools.Utils
import pfDevTools.Git

from pfDevTools.Exceptions import ArgumentError


# -- Classes
class Clone:
    """A tool to clone the Github core template."""

    def __init__(self, arguments, debug_on: bool = False):
        """Constructor based on command line arguments."""

        self._debug_on: bool = debug_on
        self._destination_folder: str = None
        self._tag_name: str = None
        self._url: str = 'github.com/DidierMalenfant/pfCoreTemplate'

        nb_of_arguments = len(arguments)
        while nb_of_arguments:
            if nb_of_arguments == 1:
                self._destination_folder: str = arguments[0]
            elif arguments[0].startswith('tag='):
                self._tag_name = arguments[0][4:]
            else:
                self._url: str = arguments[0]

            nb_of_arguments -= 1
            arguments = arguments[1:]

        if self._destination_folder is None:
            raise ArgumentError('Invalid arguments. Maybe start with `pf --help?')

    def run(self) -> None:
        try:
            if os.path.exists(self._destination_folder):
                raise RuntimeError('Folder \'' + self._destination_folder + '\' already exists.')

            print(f'Cloning core template in \'{self._destination_folder}\'.')

            pfDevTools.Git(self._url).cloneIn(self._destination_folder, self._tag_name)

            git_folder = os.path.join(self._destination_folder, '.git')
            if os.path.exists(git_folder):
                pfDevTools.Utils.deleteFolder(git_folder, force_delete=True)
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
        return 'clone'

    @classmethod
    def usage(cls) -> None:
        print('   clone <url> <tag=name> dest_folder    - Clone core template repo or repo at url optionally at a given tag/branch.')
        print('                                           (url defaults to pfCoreTemplate\'s repo if missing).')
