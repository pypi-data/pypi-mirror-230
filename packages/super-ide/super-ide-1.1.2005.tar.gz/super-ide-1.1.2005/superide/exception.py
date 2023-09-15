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


class PlatformioException(Exception):
    MESSAGE = None

    def __str__(self):  # pragma: no cover
        if self.MESSAGE:
            # pylint: disable=not-an-iterable
            return self.MESSAGE.format(*self.args)

        return super().__str__()


class ReturnErrorCode(PlatformioException):
    MESSAGE = "{0}"


class UserSideException(PlatformioException):
    pass


class AbortedByUser(UserSideException):
    MESSAGE = "Aborted by user"


#
# UDEV Rules
#


class InvalidUdevRules(UserSideException):
    pass


class MissedUdevRules(InvalidUdevRules):
    MESSAGE = (
        "Warning! Please install `99-superide-udev.rules`. \nMore details: "
        "https://docs.superide.org/en/latest/core/installation/udev-rules.html"
    )


class OutdatedUdevRules(InvalidUdevRules):
    MESSAGE = (
        "Warning! Your `{0}` are outdated. Please update or reinstall them."
        "\nMore details: "
        "https://docs.superide.org/en/latest/core/installation/udev-rules.html"
    )


#
# Misc
#


class GetSerialPortsError(PlatformioException):
    MESSAGE = "No implementation for your platform ('{0}') available"


class GetLatestVersionError(PlatformioException):
    MESSAGE = "Can not retrieve the latest superide version"


class InvalidSettingName(UserSideException):
    MESSAGE = "Invalid setting with the name '{0}'"


class InvalidSettingValue(UserSideException):
    MESSAGE = "Invalid value '{0}' for the setting '{1}'"


class InvalidJSONFile(ValueError, UserSideException):
    MESSAGE = "Could not load broken JSON: {0}"


class CIBuildEnvsEmpty(UserSideException):
    MESSAGE = (
        "Can't find superide build environments.\n"
        "Please specify `--board` or path to `platformio.ini` with "
        "predefined environments using `--project-conf` option"
    )


class HomeDirPermissionsError(UserSideException):
    MESSAGE = (
        "The directory `{0}` or its parent directory is not owned by the "
        "current user and superide can not store configuration data.\n"
        "Please check the permissions and owner of that directory.\n"
        "Otherwise, please remove manually `{0}` directory and superide "
        "will create new from the current user."
    )


class CygwinEnvDetected(PlatformioException):
    MESSAGE = (
        "superide does not work within Cygwin environment. "
        "Use native Terminal instead."
    )
