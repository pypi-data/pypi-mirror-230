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

from superide import util
from superide.exception import UserSideException


class PackageException(UserSideException):
    pass


class ManifestException(PackageException):
    pass


class UnknownManifestError(ManifestException):
    pass


class ManifestParserError(ManifestException):
    pass


class ManifestValidationError(ManifestException):
    def __init__(self, messages, data, valid_data):
        super().__init__()
        self.messages = messages
        self.data = data
        self.valid_data = valid_data

    def __str__(self):
        return (
            "Invalid manifest fields: %s. \nPlease check specification -> "
            "https://docs.superide.org/page/librarymanager/config.html"
            % self.messages
        )


class MissingPackageManifestError(ManifestException):
    MESSAGE = "Could not find one of '{0}' manifest files in the package"


class UnknownPackageError(PackageException):
    MESSAGE = (
        "Could not find the package with '{0}' requirements for your system '%s'"
        % util.get_systype()
    )


class NotGlobalLibDir(PackageException):
    MESSAGE = (
        "The `{0}` is not a superide project.\n\n"
        "To manage libraries in global storage `{1}`,\n"
        "please use `superide lib --global {2}` or specify custom storage "
        "`superide lib --storage-dir /path/to/storage/ {2}`.\n"
        "Check `superide lib --help` for details."
    )
