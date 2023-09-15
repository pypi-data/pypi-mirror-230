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


@click.command("destroy", short_help="Destroy organization")
@click.argument("orgname")
def org_destroy_cmd(orgname):
    client = AccountClient()
    click.confirm(
        "Are you sure you want to delete the `%s` organization account?\n"
        "Warning! All linked data will be permanently removed and can not be restored."
        % orgname,
        abort=True,
    )
    client.destroy_org(orgname)
    return click.secho(
        "Organization `%s` has been destroyed." % orgname,
        fg="green",
    )
