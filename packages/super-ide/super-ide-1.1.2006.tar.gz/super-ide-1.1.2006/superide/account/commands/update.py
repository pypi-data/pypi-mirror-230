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

from superide.account.client import AccountClient, AccountNotAuthorized
from superide.account.validate import validate_email, validate_username


@click.command("update", short_help="Update profile information")
@click.option("--current-password", prompt=True, hide_input=True)
@click.option("--username")
@click.option("--email")
@click.option("--firstname")
@click.option("--lastname")
def account_update_cmd(current_password, **kwargs):
    client = AccountClient()
    profile = client.get_profile()
    new_profile = profile.copy()
    if not any(kwargs.values()):
        for field in profile:
            new_profile[field] = click.prompt(
                field.replace("_", " ").capitalize(), default=profile[field]
            )
            if field == "email":
                validate_email(new_profile[field])
            if field == "username":
                validate_username(new_profile[field])
    else:
        new_profile.update({key: value for key, value in kwargs.items() if value})
    client.update_profile(new_profile, current_password)
    click.secho("Profile successfully updated!", fg="green")
    username_changed = new_profile["username"] != profile["username"]
    email_changed = new_profile["email"] != profile["email"]
    if not username_changed and not email_changed:
        return None
    try:
        client.logout()
    except AccountNotAuthorized:
        pass
    if email_changed:
        click.secho(
            "Please check your mail to verify your new email address and re-login. ",
            fg="yellow",
        )
        return None
    click.secho("Please re-login.", fg="yellow")
    return None
