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

import pfDevTools.OpenFPGACore

import SCons.Environment
import SCons.Script


def SConsEnvironment(**kwargs):
    SCons.Script.AddOption(
        '--skip_build',
        action='store_true',
        help='Skip building the core',
        default=False
    )
    SCons.Script.AddOption(
        '--debug_on',
        action='store_true',
        help='Enable debugging information',
        default=False
    )

    env = SCons.Environment.Environment(**kwargs)

    env.AddMethod(pfDevTools.OpenFPGACore.build, 'OpenFPGACore')

    if SCons.Script.GetOption('skip_build'):
        env['PF_SKIP_BUILD'] = True

    if SCons.Script.GetOption('debug_on'):
        env['PF_DEBUG_ON'] = True

    return env
