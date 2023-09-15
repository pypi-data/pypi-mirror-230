# Copyright (c) Mengning Software. 2023. All rights reserved.
#
# Super IDE licensed under GNU Affero General Public License v3 (AGPL-3.0) .
# You can use this software according to the terms and conditions of the AGPL-3.0.
# You may obtain a copy of AGPL-3.0 at:
#
#    https://www.gnu.org/licenses/agpl-3.0.txt
#
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the AGPL-3.0 for more details.

from superide.exception import UserSideException


class PlatformException(UserSideException):
    pass


class UnknownPlatform(PlatformException):
    MESSAGE = "Unknown development platform '{0}'"


class IncompatiblePlatform(PlatformException):
    MESSAGE = (
        "Development platform '{0}' is not compatible with superide Core v{1} and "
        "depends on superide Core {2}.\n"
    )


class UnknownBoard(PlatformException):
    MESSAGE = "Unknown board ID '{0}'"


class InvalidBoardManifest(PlatformException):
    MESSAGE = "Invalid board JSON manifest '{0}'"


class UnknownFramework(PlatformException):
    MESSAGE = "Unknown framework '{0}'"


class BuildScriptNotFound(PlatformException):
    MESSAGE = "Invalid path '{0}' to build script"
