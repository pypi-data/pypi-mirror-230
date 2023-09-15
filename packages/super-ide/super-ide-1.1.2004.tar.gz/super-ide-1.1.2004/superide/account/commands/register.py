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

import click

from superide.account.client import AccountClient
from superide.account.validate import (
    validate_email,
    validate_password,
    validate_username,
)


@click.command("register", short_help="Create new superide Account")
@click.option(
    "-u",
    "--username",
    prompt=True,
    callback=lambda _, __, value: validate_username(value),
)
@click.option(
    "-e", "--email", prompt=True, callback=lambda _, __, value: validate_email(value)
)
@click.option(
    "-p",
    "--password",
    prompt=True,
    hide_input=True,
    confirmation_prompt=True,
    callback=lambda _, __, value: validate_password(value),
)
@click.option("--firstname", prompt=True)
@click.option("--lastname", prompt=True)
def account_register_cmd(username, email, password, firstname, lastname):
    client = AccountClient()
    client.registration(username, email, password, firstname, lastname)
    click.secho(
        "An account has been successfully created. "
        "Please check your mail to activate your account and verify your email address.",
        fg="green",
    )
