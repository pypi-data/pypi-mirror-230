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

import json

import click

from superide.remote.client.base import RemoteClientBase


class DeviceListClient(RemoteClientBase):
    def __init__(self, agents, json_output):
        RemoteClientBase.__init__(self)
        self.agents = agents
        self.json_output = json_output

    def agent_pool_ready(self):
        d = self.agentpool.callRemote("cmd", self.agents, "device.list")
        d.addCallback(self._cbResult)
        d.addErrback(self.cb_global_error)

    def _cbResult(self, result):
        data = {}
        for success, value in result:
            if not success:
                click.secho(value, fg="red", err=True)
                continue
            (agent_name, devlist) = value
            data[agent_name] = devlist

        if self.json_output:
            click.echo(json.dumps(data))
        else:
            for agent_name, devlist in data.items():
                click.echo("Agent %s" % click.style(agent_name, fg="cyan", bold=True))
                click.echo("=" * (6 + len(agent_name)))
                for item in devlist:
                    click.secho(item["port"], fg="cyan")
                    click.echo("-" * len(item["port"]))
                    click.echo("Hardware ID: %s" % item["hwid"])
                    click.echo("Description: %s" % item["description"])
                    click.echo("")
        self.disconnect()
