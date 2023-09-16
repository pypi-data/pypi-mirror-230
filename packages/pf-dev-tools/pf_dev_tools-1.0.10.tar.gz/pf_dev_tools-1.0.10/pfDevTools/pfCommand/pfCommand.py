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
import getopt
import pfDevTools.Utils
import pfDevTools.Git

from semver import Version
from pathlib import Path

from pfDevTools.__about__ import __version__
from pfDevTools.Exceptions import ArgumentError

from .Clean import Clean
from .Clone import Clone
from .Convert import Convert
from .Delete import Delete
from .DryRun import DryRun
from .Eject import Eject
from .Install import Install
from .Make import Make
from .Qfs import Qfs
from .Reverse import Reverse


# -- Classes
class pfCommand:
    """The pf command line tool for Project Freedom."""

    def __init__(self, args):
        """Constructor based on command line arguments."""

        try:
            self._commands = [Clean, Clone, Convert, Delete, DryRun, Eject, Install, Make, Qfs, Reverse]
            self._debug_on = False

            # -- Gather the arguments
            opts, arguments = getopt.getopt(args, 'dhv', ['debug', 'help', 'version'])

            for o, a in opts:
                if o in ('-d', '--debug'):
                    self._debug_on = True
                elif o in ('-h', '--help'):
                    self.printUsage()
                    sys.exit(0)
                elif o in ('-v', '--version'):
                    pfCommand.printVersion()
                    sys.exit(0)

            if len(arguments) == 0:
                raise ArgumentError('Invalid arguments. Maybe start with `pf --help?')

            self._command_found = None
            for command in self._commands:
                if command.name() == arguments[0]:
                    self._command_found = command
                    break

            if self._command_found is None:
                raise ArgumentError(f'Unknown command \'{arguments[0]}\'. Maybe start with `pf --help?')

            self._arguments = arguments[1:]

        except getopt.GetoptError:
            print('Unknown option. Maybe start with `pf --help?')
            sys.exit(0)

    def main(self) -> None:
        self._command_found(self._arguments, debug_on=self._debug_on).run()

        pfCommand.checkForUpdates()

    def printUsage(self) -> None:
        pfCommand.printVersion()
        print('')
        print('usage: pf <options> command <arguments>')
        print('')
        print('The following options are supported:')
        print('')
        print('   --help/-h                             - Show a help message.')
        print('   --version/-v                          - Display the app\'s version.')
        print('   --debug/-d                            - Enable extra debugging information.')
        print('')
        print('Supported commands are:')

        for command in self._commands:
            command.usage()

        print('')

    @classmethod
    def printVersion(cls) -> None:
        print('👾 pf-dev-tools v' + __version__ + ' 👾')

        pfCommand.checkForUpdates()

    @classmethod
    def checkForUpdates(cls, force_check=False):
        try:
            file_path = pfDevTools.Paths.appUpdateCheckFile()
            if not force_check and not pfDevTools.Utils.fileOlderThan(file_path, time_in_seconds=(24 * 60 * 60)):
                return

            latest_version = pfDevTools.Git('github.com/DidierMalenfant/pfDevTools').getLatestVersion()
            if latest_version is None:
                return

            os.makedirs(Path(file_path).parent, exist_ok=True)

            if os.path.exists(file_path):
                os.remove(file_path)

            with open(file_path, 'w') as out_file:
                out_file.write('check')

            if latest_version > Version.parse(__version__):
                warning = '‼️' if sys.platform == "darwin" else '!!'
                print(f'{warning}  Version v{str(latest_version)} is available for pf-dev-tools. You have v{__version__} {warning}')
                print('Please run \'pip install pf-dev-tools --upgrade\' to upgrade.')
        except Exception:
            pass
