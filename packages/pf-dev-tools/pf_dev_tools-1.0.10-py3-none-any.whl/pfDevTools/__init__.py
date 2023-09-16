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

from .pfCommand.Clean import Clean
from .pfCommand.Clone import Clone
from .pfCommand.Convert import Convert
from .pfCommand.Delete import Delete
from .pfCommand.DryRun import DryRun
from .pfCommand.Eject import Eject
from .pfCommand.Install import Install
from .pfCommand.Make import Make
from .pfCommand.Qfs import Qfs
from .pfCommand.Reverse import Reverse

from .Package import Package
from .CoreConfig import CoreConfig
from .Git import Git
from .Paths import Paths
from .SCons import SConsEnvironment
from .Utils import Utils

from semver import Version

from .__about__ import __version__


# --- Makes sure current pfDevTools versions is supported
def requires(version: str) -> bool:
    current = Version.parse(__version__, optional_minor_and_patch=True)
    required = Version.parse(version, optional_minor_and_patch=True)

    if not (required.major == current.major) and ((current.minor > required.minor) or ((current.minor == required.minor) and (current.patch >= required.patch))) and (required.prerelease == current.prerelease):
        raise RuntimeError(f'pfDevTools v{str(current)} is not compatible with the required version v{str(required)}.')
