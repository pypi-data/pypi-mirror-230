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

import math

import click

from superide import util
from superide.registry.client import RegistryClient


@click.command("search", short_help="Search for packages")
@click.argument("query")
@click.option("-p", "--page", type=click.IntRange(min=1))
@click.option(
    "-s",
    "--sort",
    type=click.Choice(["relevance", "popularity", "trending", "added", "updated"]),
)
def package_search_cmd(query, page, sort):
    client = RegistryClient()
    result = client.list_packages(query, page=page, sort=sort)
    if not result["total"]:
        click.secho("Nothing has been found by your request", fg="yellow")
        click.echo(
            "Try a less-specific search or use truncation (or wildcard) operator *"
        )
        return
    print_search_result(result)


def print_search_result(result):
    click.echo(
        "Found %d packages (page %d of %d)"
        % (
            result["total"],
            result["page"],
            math.ceil(result["total"] / result["limit"]),
        )
    )
    for item in result["items"]:
        click.echo()
        print_search_item(item)


def print_search_item(item):
    click.echo(
        "%s/%s"
        % (
            click.style(item["owner"]["username"], fg="cyan"),
            click.style(item["name"], fg="cyan", bold=True),
        )
    )
    click.echo(
        "%s • %s • Published on %s"
        % (
            item["type"].capitalize()
            if item["tier"] == "community"
            else click.style(
                ("%s %s" % (item["tier"], item["type"])).title(), bold=True
            ),
            item["version"]["name"],
            util.parse_datetime(item["version"]["released_at"]).strftime("%c"),
        )
    )
    click.echo(item["description"])
