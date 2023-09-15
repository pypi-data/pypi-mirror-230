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


@click.command("destroy", short_help="Destroy account")
def account_destroy_cmd():
    client = AccountClient()
    click.confirm(
        "Are you sure you want to delete the %s user account?\n"
        "Warning! All linked data will be permanently removed and can not be restored."
        % client.get_logged_username(),
        abort=True,
    )
    client.destroy_account()
    try:
        client.logout()
    except AccountNotAuthorized:
        pass
    click.secho(
        "User account has been destroyed.",
        fg="green",
    )
