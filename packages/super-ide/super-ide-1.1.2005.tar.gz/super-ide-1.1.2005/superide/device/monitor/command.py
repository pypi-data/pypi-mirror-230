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

import os
import sys

import click

from superide import exception, fs
from superide.device.finder import SerialPortFinder
from superide.device.monitor.filters.base import register_filters
from superide.device.monitor.terminal import get_available_filters, start_terminal
from superide.platform.factory import PlatformFactory
from superide.project.config import ProjectConfig
from superide.project.exception import NotPlatformIOProjectError
from superide.project.options import ProjectOptions


@click.command("monitor", short_help="Monitor device (Serial/Socket)")
@click.option("--port", "-p", help="Port, a number or a device name")
@click.option(
    "-b",
    "--baud",
    type=ProjectOptions["env.monitor_speed"].type,
    help="Set baud/speed [default=%d]" % ProjectOptions["env.monitor_speed"].default,
)
@click.option(
    "--parity",
    type=ProjectOptions["env.monitor_parity"].type,
    help="Enable parity checking [default=%s]"
    % ProjectOptions["env.monitor_parity"].default,
)
@click.option("--rtscts", is_flag=True, help="Enable RTS/CTS flow control")
@click.option("--xonxoff", is_flag=True, help="Enable software flow control")
@click.option(
    "--rts",
    type=ProjectOptions["env.monitor_rts"].type,
    help="Set initial RTS line state",
)
@click.option(
    "--dtr",
    type=ProjectOptions["env.monitor_dtr"].type,
    help="Set initial DTR line state",
)
@click.option("--echo", is_flag=True, help="Enable local echo")
@click.option(
    "--encoding",
    help=(
        "Set the encoding for the serial port "
        "(e.g. hexlify, Latin1, UTF-8) [default=%s]"
        % ProjectOptions["env.monitor_encoding"].default
    ),
)
@click.option(
    "-f",
    "--filter",
    "filters",
    multiple=True,
    help="Apply filters/text transformations",
)
@click.option(
    "--eol",
    type=ProjectOptions["env.monitor_eol"].type,
    help="End of line mode [default=%s]" % ProjectOptions["env.monitor_eol"].default,
)
@click.option("--raw", is_flag=True, help=ProjectOptions["env.monitor_raw"].description)
@click.option(
    "--exit-char",
    type=int,
    default=3,
    show_default=True,
    help="ASCII code of special character that is used to exit "
    "the application [default=3 (Ctrl+C)]",
)
@click.option(
    "--menu-char",
    type=int,
    default=20,
    help="ASCII code of special character that is used to "
    "control terminal (menu) [default=20 (DEC)]",
)
@click.option(
    "--quiet",
    is_flag=True,
    help="Diagnostics: suppress non-error messages",
)
@click.option(
    "--no-reconnect",
    is_flag=True,
    help="Disable automatic reconnection if the established connection fails",
)
@click.option(
    "-d",
    "--project-dir",
    default=os.getcwd,
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
)
@click.option(
    "-e",
    "--environment",
    help="Load configuration from `platformio.ini` and the specified environment",
)
def device_monitor_cmd(**options):
    with fs.cd(options["project_dir"]):
        platform = None
        project_options = {}
        try:
            project_options = get_project_options(options["environment"])
            if "platform" in project_options:
                platform = PlatformFactory.new(project_options["platform"])
        except NotPlatformIOProjectError:
            pass

        options = apply_project_monitor_options(options, project_options)
        register_filters(platform=platform, options=options)
        options["port"] = SerialPortFinder(
            board_config=platform.board_config(project_options.get("board"))
            if platform and project_options.get("board")
            else None,
            upload_protocol=project_options.get("upload_protocol"),
            ensure_ready=True,
        ).find(initial_port=options["port"])

        if options["menu_char"] == options["exit_char"]:
            raise exception.UserSideException(
                "--exit-char can not be the same as --menu-char"
            )

        # check for unknown filters
        if options["filters"]:
            known_filters = set(get_available_filters())
            unknown_filters = set(options["filters"]) - known_filters
            if unknown_filters:
                options["filters"] = list(known_filters & set(options["filters"]))
                click.secho(
                    ("Warning! Skipping unknown filters `%s`. Known filters are `%s`")
                    % (", ".join(unknown_filters), ", ".join(sorted(known_filters))),
                    fg="yellow",
                )

        start_terminal(options)


def get_project_options(environment=None):
    config = ProjectConfig.get_instance()
    config.validate(envs=[environment] if environment else None)
    environment = environment or config.get_default_env()
    return config.items(env=environment, as_dict=True)


def apply_project_monitor_options(initial_options, project_options):
    for option_meta in ProjectOptions.values():
        if option_meta.group != "monitor":
            continue
        cli_key = option_meta.name.split("_", 1)[1]
        if cli_key == "speed":
            cli_key = "baud"
        # value set from CLI, skip overriding
        if initial_options[cli_key] not in (None, (), []) and (
            option_meta.type != click.BOOL or f"--{cli_key}" in sys.argv[1:]
        ):
            continue
        initial_options[cli_key] = project_options.get(
            option_meta.name, option_meta.default
        )
    return initial_options
