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

import sys
import traceback

from .pfCommand import pfCommand
from pfDevTools.Exceptions import ArgumentError

# -- This enables more debugging information for exceptions.
_debug_on: bool = False


def main():
    global _debug_on

    try:
        if '--debug' in sys.argv:
            print('Enabling debugging information.')
            _debug_on = True

        # -- Remove the first argument (which is the script filename)
        pfCommand(sys.argv[1:]).main()
    except ArgumentError as e:
        error_string = str(e)

        if len(error_string) != 0:
            print(e)

        sys.exit(1)
    except Exception as e:
        if _debug_on is True:
            print(traceback.format_exc())
        else:
            error_string = str(e)

            if len(error_string) != 0:
                print(e)

        sys.exit(1)
    except KeyboardInterrupt:
        print('Execution interrupted by user.')
        sys.exit(1)


if __name__ == '__main__':
    main()
