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

import click

from superide.account.validate import validate_orgname_teamname, validate_username


def validate_urn(value):
    value = str(value).strip()
    if not re.match(r"^prn:reg:pkg:(\d+):(\w+)$", value, flags=re.I):
        raise click.BadParameter("Invalid URN format.")
    return value


def validate_client(value):
    if ":" in value:
        validate_orgname_teamname(value)
    else:
        validate_username(value)
    return value
