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


def validate_username(value, field="username"):
    value = str(value).strip() if value else None
    if not value or not re.match(
        r"^[a-z\d](?:[a-z\d]|-(?=[a-z\d])){0,37}$", value, flags=re.I
    ):
        raise click.BadParameter(
            "Invalid %s format. "
            "%s must contain only alphanumeric characters "
            "or single hyphens, cannot begin or end with a hyphen, "
            "and must not be longer than 38 characters."
            % (field.lower(), field.capitalize())
        )
    return value


def validate_orgname(value):
    return validate_username(value, "Organization name")


def validate_email(value):
    value = str(value).strip() if value else None
    if not value or not re.match(
        r"^[a-z\d_\.\+\-]+@[a-z\d\-]+\.[a-z\d\-\.]+$", value, flags=re.I
    ):
        raise click.BadParameter("Invalid email address")
    return value


def validate_password(value):
    value = str(value).strip() if value else None
    if not value or not re.match(r"^(?=.*[a-z])(?=.*\d).{8,}$", value):
        raise click.BadParameter(
            "Invalid password format. "
            "Password must contain at least 8 characters"
            " including a number and a lowercase letter"
        )
    return value


def validate_teamname(value):
    value = str(value).strip() if value else None
    if not value or not re.match(
        r"^[a-z\d](?:[a-z\d]|[\-_ ](?=[a-z\d])){0,19}$", value, flags=re.I
    ):
        raise click.BadParameter(
            "Invalid team name format. "
            "Team name must only contain alphanumeric characters, "
            "single hyphens, underscores, spaces. It can not "
            "begin or end with a hyphen or a underscore and must"
            " not be longer than 20 characters."
        )
    return value


def validate_orgname_teamname(value):
    value = str(value).strip() if value else None
    if not value or ":" not in value:
        raise click.BadParameter(
            "Please specify organization and team name using the following"
            " format - orgname:teamname. For example, mycompany:DreamTeam"
        )
    orgname, teamname = value.split(":", 1)
    validate_orgname(orgname)
    validate_teamname(teamname)
    return value
