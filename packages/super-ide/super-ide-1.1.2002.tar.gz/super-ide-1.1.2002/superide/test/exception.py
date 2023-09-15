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


class UnitTestError(PlatformioException):
    pass


class TestDirNotExistsError(UnitTestError, UserSideException):
    MESSAGE = (
        "A test folder '{0}' does not exist.\nPlease create 'test' "
        "directory in the project root and put a test suite.\n"
        "More details about Unit "
        "Testing: https://docs.superide.org/en/latest/advanced/"
        "unit-testing/index.html"
    )


class UnitTestSuiteError(UnitTestError):
    pass
