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

from datetime import datetime

import click

from superide.remote.client.base import RemoteClientBase


class AgentListClient(RemoteClientBase):
    def agent_pool_ready(self):
        d = self.agentpool.callRemote("list", True)
        d.addCallback(self._cbResult)
        d.addErrback(self.cb_global_error)

    def _cbResult(self, result):
        for item in result:
            click.secho(item["name"], fg="cyan")
            click.echo("-" * len(item["name"]))
            click.echo("ID: %s" % item["id"])
            click.echo(
                "Started: %s"
                % datetime.fromtimestamp(item["started"]).strftime("%Y-%m-%d %H:%M:%S")
            )
            click.echo("")
        self.disconnect()
