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

from superide import fs
from superide.system.prune import (
    prune_cached_data,
    prune_core_packages,
    prune_platform_packages,
)


@click.command("prune", short_help="Remove unused data")
@click.option("--force", "-f", is_flag=True, help="Do not prompt for confirmation")
@click.option(
    "--dry-run", is_flag=True, help="Do not prune, only show data that will be removed"
)
@click.option("--cache", is_flag=True, help="Prune only cached data")
@click.option(
    "--core-packages", is_flag=True, help="Prune only unnecessary core packages"
)
@click.option(
    "--platform-packages",
    is_flag=True,
    help="Prune only unnecessary development platform packages",
)
def system_prune_cmd(force, dry_run, cache, core_packages, platform_packages):
    if dry_run:
        click.secho(
            "Dry run mode (do not prune, only show data that will be removed)",
            fg="yellow",
        )
        click.echo()

    reclaimed_cache = 0
    reclaimed_core_packages = 0
    reclaimed_platform_packages = 0
    prune_all = not any([cache, core_packages, platform_packages])

    if cache or prune_all:
        reclaimed_cache = prune_cached_data(force, dry_run)
        click.echo()

    if core_packages or prune_all:
        reclaimed_core_packages = prune_core_packages(force, dry_run)
        click.echo()

    if platform_packages or prune_all:
        reclaimed_platform_packages = prune_platform_packages(force, dry_run)
        click.echo()

    click.secho(
        "Total reclaimed space: %s"
        % fs.humanize_file_size(
            reclaimed_cache + reclaimed_core_packages + reclaimed_platform_packages
        ),
        fg="green",
    )
