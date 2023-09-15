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

import logging
import os

import click

from superide import fs
from superide.package.manager.library import LibraryPackageManager
from superide.package.manager.platform import PlatformPackageManager
from superide.package.manager.tool import ToolPackageManager
from superide.package.meta import PackageSpec
from superide.project.config import ProjectConfig
from superide.project.savedeps import pkg_to_save_spec, save_project_dependencies


@click.command(
    "uninstall", short_help="Uninstall the project dependencies or custom packages"
)
@click.option(
    "-d",
    "--project-dir",
    default=os.getcwd,
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
)
@click.option("-e", "--environment", "environments", multiple=True)
@click.option("-p", "--platform", "platforms", metavar="SPECIFICATION", multiple=True)
@click.option("-t", "--tool", "tools", metavar="SPECIFICATION", multiple=True)
@click.option("-l", "--library", "libraries", metavar="SPECIFICATION", multiple=True)
@click.option(
    "--no-save",
    is_flag=True,
    help="Prevent removing specified packages from `platformio.ini`",
)
@click.option("--skip-dependencies", is_flag=True, help="Skip package dependencies")
@click.option("-g", "--global", is_flag=True, help="Uninstall global packages")
@click.option(
    "--storage-dir",
    default=None,
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    help="Custom Package Manager storage for global packages",
)
@click.option("-s", "--silent", is_flag=True, help="Suppress progress reporting")
def package_uninstall_cmd(**options):
    if options.get("global"):
        uninstall_global_dependencies(options)
    else:
        uninstall_project_dependencies(options)


def uninstall_global_dependencies(options):
    pm = PlatformPackageManager(options.get("storage_dir"))
    tm = ToolPackageManager(options.get("storage_dir"))
    lm = LibraryPackageManager(options.get("storage_dir"))
    for obj in (pm, tm, lm):
        obj.set_log_level(logging.WARN if options.get("silent") else logging.DEBUG)
    for spec in options.get("platforms"):
        pm.uninstall(
            spec,
            skip_dependencies=options.get("skip_dependencies"),
        )
    for spec in options.get("tools"):
        tm.uninstall(
            spec,
            skip_dependencies=options.get("skip_dependencies"),
        )
    for spec in options.get("libraries", []):
        lm.uninstall(
            spec,
            skip_dependencies=options.get("skip_dependencies"),
        )


def uninstall_project_dependencies(options):
    environments = options["environments"]
    with fs.cd(options["project_dir"]):
        config = ProjectConfig.get_instance()
        config.validate(environments)
        for env in config.envs():
            if environments and env not in environments:
                continue
            if not options["silent"]:
                click.echo("Resolving %s dependencies..." % click.style(env, fg="cyan"))
            already_up_to_date = not uninstall_project_env_dependencies(env, options)
            if not options["silent"] and already_up_to_date:
                click.secho("Already up-to-date.", fg="green")


def uninstall_project_env_dependencies(project_env, options=None):
    options = options or {}
    uninstalled_conds = []
    # custom platforms
    if options.get("platforms"):
        uninstalled_conds.append(
            _uninstall_project_env_custom_platforms(project_env, options)
        )
    # custom tools
    if options.get("tools"):
        uninstalled_conds.append(
            _uninstall_project_env_custom_tools(project_env, options)
        )
    # custom ibraries
    if options.get("libraries"):
        uninstalled_conds.append(
            _uninstall_project_env_custom_libraries(project_env, options)
        )
    # declared dependencies
    if not uninstalled_conds:
        uninstalled_conds = [
            _uninstall_project_env_platform(project_env, options),
            _uninstall_project_env_libraries(project_env, options),
        ]
    return any(uninstalled_conds)


def _uninstall_project_env_platform(project_env, options):
    config = ProjectConfig.get_instance()
    pm = PlatformPackageManager()
    if options.get("silent"):
        pm.set_log_level(logging.WARN)
    spec = config.get(f"env:{project_env}", "platform")
    if not spec:
        return None
    already_up_to_date = True
    if not pm.get_package(spec):
        return None
    PlatformPackageManager().uninstall(
        spec,
        project_env=project_env,
        skip_dependencies=options.get("skip_dependencies"),
    )
    return not already_up_to_date


def _uninstall_project_env_custom_platforms(project_env, options):
    already_up_to_date = True
    pm = PlatformPackageManager()
    if not options.get("silent"):
        pm.set_log_level(logging.DEBUG)
    for spec in options.get("platforms"):
        if pm.get_package(spec):
            already_up_to_date = False
        pm.uninstall(
            spec,
            project_env=project_env,
            skip_dependencies=options.get("skip_dependencies"),
        )
    return not already_up_to_date


def _uninstall_project_env_custom_tools(project_env, options):
    already_up_to_date = True
    tm = ToolPackageManager()
    if not options.get("silent"):
        tm.set_log_level(logging.DEBUG)
    specs_to_save = []
    for tool in options.get("tools"):
        spec = PackageSpec(tool)
        if tm.get_package(spec):
            already_up_to_date = False
        pkg = tm.uninstall(
            spec,
            skip_dependencies=options.get("skip_dependencies"),
        )
        specs_to_save.append(pkg_to_save_spec(pkg, spec))
    if not options.get("no_save") and specs_to_save:
        save_project_dependencies(
            os.getcwd(),
            specs_to_save,
            scope="platform_packages",
            action="remove",
            environments=[project_env],
        )
    return not already_up_to_date


def _uninstall_project_env_libraries(project_env, options):
    already_up_to_date = True
    config = ProjectConfig.get_instance()
    lm = LibraryPackageManager(
        os.path.join(config.get("superide", "libdeps_dir"), project_env)
    )
    if options.get("silent"):
        lm.set_log_level(logging.WARN)
    for library in config.get(f"env:{project_env}", "lib_deps"):
        spec = PackageSpec(library)
        # skip built-in dependencies
        if not spec.external and not spec.owner:
            continue
        if lm.get_package(spec):
            already_up_to_date = False
            lm.uninstall(
                spec,
                skip_dependencies=options.get("skip_dependencies"),
            )
    return not already_up_to_date


def _uninstall_project_env_custom_libraries(project_env, options):
    already_up_to_date = True
    config = ProjectConfig.get_instance()
    lm = LibraryPackageManager(
        os.path.join(config.get("superide", "libdeps_dir"), project_env)
    )
    if not options.get("silent"):
        lm.set_log_level(logging.DEBUG)
    specs_to_save = []
    for library in options.get("libraries") or []:
        spec = PackageSpec(library)
        if lm.get_package(spec):
            already_up_to_date = False
        pkg = lm.uninstall(
            spec,
            skip_dependencies=options.get("skip_dependencies"),
        )
        specs_to_save.append(pkg_to_save_spec(pkg, spec))
    if not options.get("no_save") and specs_to_save:
        save_project_dependencies(
            os.getcwd(),
            specs_to_save,
            scope="lib_deps",
            action="remove",
            environments=[project_env],
        )
    return not already_up_to_date
