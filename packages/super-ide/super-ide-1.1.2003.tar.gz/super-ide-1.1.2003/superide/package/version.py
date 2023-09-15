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

import re

import semantic_version

from superide.exception import UserSideException


class SemanticVersionError(UserSideException):
    pass


def cast_version_to_semver(value, force=True, raise_exception=False):
    assert value
    try:
        return semantic_version.Version(value)
    except ValueError:
        pass
    if force:
        try:
            return semantic_version.Version.coerce(value)
        except ValueError:
            pass
    if raise_exception:
        raise SemanticVersionError("Invalid SemVer version %s" % value)
    # parse commit hash
    if re.match(r"^[\da-f]+$", value, flags=re.I):
        return semantic_version.Version("0.0.0+sha." + value)
    return semantic_version.Version("0.0.0+" + value)


def pepver_to_semver(pepver):
    return cast_version_to_semver(
        re.sub(r"(\.\d+)\.?(dev|a|b|rc|post)", r"\1-\2.", pepver, 1)
    )


def get_original_version(version):
    if version.count(".") != 2:
        return None
    _, raw = version.split(".")[:2]
    if int(raw) <= 99:
        return None
    if int(raw) <= 9999:
        return "%s.%s" % (raw[:-2], int(raw[-2:]))
    return "%s.%s.%s" % (raw[:-4], int(raw[-4:-2]), int(raw[-2:]))
