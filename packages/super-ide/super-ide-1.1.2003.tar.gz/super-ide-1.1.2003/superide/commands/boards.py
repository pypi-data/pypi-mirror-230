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
import shutil

import click
from tabulate import tabulate

from superide import fs
from superide.package.manager.platform import PlatformPackageManager


@click.command("boards", short_help="Board Explorer")
@click.argument("query", required=False)
@click.option("--installed", is_flag=True)
@click.option("--json-output", is_flag=True)
def cli(query, installed, json_output):  # pylint: disable=R0912
    if json_output:
        return _print_boards_json(query, installed)

    grpboards = {}
    for board in _get_boards(installed):
        if query and not any(
            query.lower() in str(board.get(k, "")).lower()
            for k in ("id", "name", "mcu", "vendor", "platform", "frameworks")
        ):
            continue
        if board["platform"] not in grpboards:
            grpboards[board["platform"]] = []
        grpboards[board["platform"]].append(board)

    terminal_width = shutil.get_terminal_size().columns
    for platform, boards in sorted(grpboards.items()):
        click.echo("")
        click.echo("Platform: ", nl=False)
        click.secho(platform, bold=True)
        click.echo("=" * terminal_width)
        print_boards(boards)
    return True


def print_boards(boards):
    click.echo(
        tabulate(
            [
                (
                    click.style(b["id"], fg="cyan"),
                    b["mcu"],
                    "%dMHz" % (b["fcpu"] / 1000000),
                    fs.humanize_file_size(b["rom"]),
                    fs.humanize_file_size(b["ram"]),
                    b["name"],
                )
                for b in boards
            ],
            headers=["ID", "MCU", "Frequency", "Flash", "RAM", "Name"],
        )
    )


def _get_boards(installed=False):
    pm = PlatformPackageManager()
    return pm.get_installed_boards() if installed else pm.get_all_boards()


def _print_boards_json(query, installed=False):
    result = []
    for board in _get_boards(installed):
        if query:
            search_data = "%s %s" % (board["id"], json.dumps(board).lower())
            if query.lower() not in search_data.lower():
                continue
        result.append(board)
    click.echo(json.dumps(result))
