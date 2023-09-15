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
import re
import subprocess

import click

from superide import VERSION, __version__, app, exception
from superide.http import fetch_remote_content
from superide.package.manager.core import update_core_packages
from superide.proc import get_pythonexe_path

PYPI_JSON_URL = "https://pypi.org/pypi/superide/json"
DEVELOP_ZIP_URL = "https://github.com/superide/superide-core/archive/develop.zip"
DEVELOP_INIT_SCRIPT_URL = (
    "https://raw.githubusercontent.com/superide/superide-core"
    "/develop/superide/__init__.py"
)


@click.command("upgrade", short_help="Upgrade superide Core to the latest version")
@click.option("--dev", is_flag=True, help="Use development branch")
@click.option("--verbose", "-v", is_flag=True)
def cli(dev, verbose):
    update_core_packages()
    if not dev and __version__ == get_latest_version():
        return click.secho(
            "You're up-to-date!\nPlatformIO %s is currently the "
            "newest version available." % __version__,
            fg="green",
        )

    click.secho("Please wait while upgrading superide Core ...", fg="yellow")

    python_exe = get_pythonexe_path()
    to_develop = dev or not all(c.isdigit() for c in __version__ if c != ".")
    pkg_spec = DEVELOP_ZIP_URL if to_develop else "superide"

    try:
        subprocess.run(
            [python_exe, "-m", "pip", "install", "--upgrade", pkg_spec],
            check=True,
            stdout=subprocess.PIPE if not verbose else None,
        )
        output = subprocess.run(
            [python_exe, "-m", "superide", "--version"],
            check=True,
            stdout=subprocess.PIPE,
        ).stdout.decode()
        assert "version" in output
        actual_version = output.split("version", 1)[1].strip()
        click.secho(
            "superide has been successfully upgraded to %s" % actual_version,
            fg="green",
        )
        click.echo("Release notes: ", nl=False)
        click.secho("https://docs.superide.org/en/latest/history.html", fg="cyan")
        if app.get_session_var("caller_id"):
            click.secho(
                "Warning! Please restart IDE to affect PIO Home changes", fg="yellow"
            )
    except (AssertionError, subprocess.CalledProcessError) as exc:
        click.secho(
            "\nWarning!!! Could not automatically upgrade the superide Core.",
            fg="red",
        )
        click.secho(
            "Please upgrade it manually using the following command:\n",
            fg="red",
        )
        click.secho(f'"{python_exe}" -m pip install -U {pkg_spec}\n', fg="cyan")
        raise exception.ReturnErrorCode(1) from exc

    return True


def get_pkg_spec(to_develop):
    if to_develop:
        return


def get_latest_version():
    try:
        if not str(VERSION[2]).isdigit():
            try:
                return get_develop_latest_version()
            except:  # pylint: disable=bare-except
                pass
        return get_pypi_latest_version()
    except Exception as exc:
        raise exception.GetLatestVersionError() from exc


def get_develop_latest_version():
    version = None
    content = fetch_remote_content(DEVELOP_INIT_SCRIPT_URL)
    for line in content.split("\n"):
        line = line.strip()
        if not line.startswith("VERSION"):
            continue
        match = re.match(r"VERSION\s*=\s*\(([^\)]+)\)", line)
        if not match:
            continue
        version = match.group(1)
        for c in (" ", "'", '"'):
            version = version.replace(c, "")
        version = ".".join(version.split(","))
    assert version
    return version


def get_pypi_latest_version():
    content = fetch_remote_content(PYPI_JSON_URL)
    return json.loads(content)["info"]["version"]
