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

from superide.exception import PlatformioException, UserSideException


class DebugError(PlatformioException):
    pass


class DebugSupportError(DebugError, UserSideException):
    MESSAGE = (
        "Currently, superide does not support debugging for `{0}`.\n"
        "Please request support at https://github.com/superide/"
        "superide-core/issues \nor visit -> https://docs.superide.org"
        "/page/plus/debugging.html"
    )


class DebugInvalidOptionsError(DebugError, UserSideException):
    pass


class DebugInitError(DebugError, UserSideException):
    pass
