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

# pylint: disable=too-many-arguments, too-many-locals
# pylint: disable=too-many-branches, too-many-statements

import asyncio
import os
import signal
import subprocess

import click

from superide import app, exception, fs, proc
from superide.compat import IS_WINDOWS
from superide.debug import helpers
from superide.debug.config.factory import DebugConfigFactory
from superide.debug.exception import DebugInvalidOptionsError
from superide.debug.process.gdb import GDBClientProcess
from superide.exception import ReturnErrorCode
from superide.platform.factory import PlatformFactory
from superide.project.config import ProjectConfig
from superide.project.helpers import is_platformio_project
from superide.project.options import ProjectOptions


@click.command(
    "debug",
    context_settings=dict(ignore_unknown_options=True),
    short_help="Unified Debugger",
)
@click.option(
    "-d",
    "--project-dir",
    default=os.getcwd,
    type=click.Path(exists=True, file_okay=False, dir_okay=True, writable=True),
)
@click.option(
    "-c",
    "--project-conf",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True),
)
@click.option("--environment", "-e", metavar="<environment>")
@click.option("--load-mode", type=ProjectOptions["env.debug_load_mode"].type)
@click.option("--verbose", "-v", is_flag=True)
@click.option("--interface", type=click.Choice(["gdb"]))
@click.argument("__unprocessed", nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def cli(
    ctx,
    project_dir,
    project_conf,
    environment,
    load_mode,
    verbose,
    interface,
    __unprocessed,
):
    app.set_session_var("custom_project_conf", project_conf)

    # use env variables from Eclipse or CLion
    for name in ("CWD", "PWD", "PLATFORMIO_PROJECT_DIR"):
        if is_platformio_project(project_dir):
            break
        if os.getenv(name):
            project_dir = os.getenv(name)

    with fs.cd(project_dir):
        project_config = ProjectConfig.get_instance(project_conf)
        project_config.validate(envs=[environment] if environment else None)
        env_name = environment or helpers.get_default_debug_env(project_config)

        if not interface:
            return helpers.predebug_project(
                ctx, project_dir, project_config, env_name, False, verbose
            )

        configure_args = (
            ctx,
            project_config,
            env_name,
            load_mode,
            verbose,
            __unprocessed,
        )
        if helpers.is_gdbmi_mode():
            os.environ["PLATFORMIO_DISABLE_PROGRESSBAR"] = "true"
            stream = helpers.GDBMIConsoleStream()
            with proc.capture_std_streams(stream):
                debug_config = _configure(*configure_args)
            stream.close()
        else:
            debug_config = _configure(*configure_args)

        _run(project_dir, debug_config, __unprocessed)

    return None


def _configure(ctx, project_config, env_name, load_mode, verbose, __unprocessed):
    platform = PlatformFactory.from_env(env_name, autoinstall=True)
    debug_config = DebugConfigFactory.new(
        platform,
        project_config,
        env_name,
    )
    if "--version" in __unprocessed:
        raise ReturnErrorCode(
            subprocess.run(
                [debug_config.client_executable_path, "--version"], check=True
            ).returncode
        )

    try:
        fs.ensure_udev_rules()
    except exception.InvalidUdevRules as exc:
        click.echo(str(exc))

    rebuild_prog = False
    preload = debug_config.load_cmds == ["preload"]
    load_mode = load_mode or debug_config.load_mode
    if load_mode == "always":
        rebuild_prog = preload or not helpers.has_debug_symbols(
            debug_config.program_path
        )
    elif load_mode == "modified":
        rebuild_prog = helpers.is_prog_obsolete(
            debug_config.program_path
        ) or not helpers.has_debug_symbols(debug_config.program_path)

    if not (debug_config.program_path and os.path.isfile(debug_config.program_path)):
        rebuild_prog = True

    if preload or (not rebuild_prog and load_mode != "always"):
        # don't load firmware through debug server
        debug_config.load_cmds = []

    if rebuild_prog:
        click.echo("Preparing firmware for debugging...")
        helpers.predebug_project(
            ctx, os.getcwd(), project_config, env_name, preload, verbose
        )
        # save SHA sum of newly created prog
        if load_mode == "modified":
            helpers.is_prog_obsolete(debug_config.program_path)

    if not os.path.isfile(debug_config.program_path):
        raise DebugInvalidOptionsError("Program/firmware is missed")

    return debug_config


def _run(project_dir, debug_config, __unprocessed):
    loop = asyncio.ProactorEventLoop() if IS_WINDOWS else asyncio.get_event_loop()
    asyncio.set_event_loop(loop)

    client = GDBClientProcess(project_dir, debug_config)
    coro = client.run(__unprocessed)
    try:
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        loop.run_until_complete(coro)
        if IS_WINDOWS:
            client.close()
            # an issue with `asyncio` executor and STIDIN,
            # it cannot be closed gracefully
            proc.force_exit()
    finally:
        client.close()
        loop.close()
