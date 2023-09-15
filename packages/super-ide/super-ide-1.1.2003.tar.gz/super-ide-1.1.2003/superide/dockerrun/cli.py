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

import mimetypes
import socket

import click
import subprocess
from superide.compat import IS_WINDOWS
from superide.home.run import run_server
from superide.package.manager.core import get_core_package_dir


@click.command("dockerrun", short_help="GUI to manage superide")
@click.option(
    "--project-dir",
    default="~/superide/Projects/test",
    help=(
        "docker run"
    ),
)
@click.option(
    "--docker-name",
    default="test",
    help=(
        "docker name"
    ),
)
def cli(project_dir,docker_name):
    try:
        result = subprocess.run(["docker", "run","-it","--rm", "-v", project_dir+":/Project", docker_name,"/root/.superide/penv/bin/pio", "run", "-d", "/Project" ], 
                                  text=True)
        if result.stdout:
            click.echo(result.stdout)
        if result.stderr:
            click.echo(f"Docker Pull Error:\n{result.stderr}")
        else:
            click.echo(f"Docker Pull failed with return code: {result.returncode}")
    except Exception as e:
        click.echo(f"Error executing the command: {e}")
