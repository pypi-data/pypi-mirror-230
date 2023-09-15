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
from typing import List

import click

from superide import fs
from superide.package.manager.library import LibraryPackageManager
from superide.package.manager.platform import PlatformPackageManager
from superide.package.manager.tool import ToolPackageManager
from superide.package.meta import PackageItem, PackageSpec
from superide.platform.exception import UnknownPlatform
from superide.platform.factory import PlatformFactory
from superide.project.config import ProjectConfig


@click.command("list", short_help="List installed packages")
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
@click.option("-g", "--global", is_flag=True, help="List globally installed packages")
@click.option(
    "--storage-dir",
    default=None,
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    help="Custom Package Manager storage for global packages",
)
@click.option("--only-platforms", is_flag=True, help="List only platform packages")
@click.option("--only-tools", is_flag=True, help="List only tool packages")
@click.option("--only-libraries", is_flag=True, help="List only library packages")
@click.option("-v", "--verbose", is_flag=True)
def package_list_cmd(**options):
    if options.get("global"):
        list_global_packages(options)
    else:
        list_project_packages(options)


def humanize_package(pkg, spec=None, verbose=False):
    if spec and not isinstance(spec, PackageSpec):
        spec = PackageSpec(spec)
    data = [
        click.style(pkg.metadata.name, fg="cyan"),
        click.style(f"@ {str(pkg.metadata.version)}", bold=True),
    ]
    extra_data = ["required: %s" % (spec.humanize() if spec else "Any")]
    if verbose:
        extra_data.append(pkg.path)
    data.append("(%s)" % ", ".join(extra_data))
    return " ".join(data)


def print_dependency_tree(pm, specs=None, filter_specs=None, level=0, verbose=False):
    filtered_pkgs = [
        pm.get_package(spec) for spec in filter_specs or [] if pm.get_package(spec)
    ]
    candidates = {}
    if specs:
        for spec in specs:
            pkg = pm.get_package(spec)
            if not pkg:
                continue
            candidates[pkg.path] = (pkg, spec)
    else:
        candidates = {pkg.path: (pkg, pkg.metadata.spec) for pkg in pm.get_installed()}
    if not candidates:
        return
    candidates = sorted(candidates.values(), key=lambda item: item[0].metadata.name)

    for index, (pkg, spec) in enumerate(candidates):
        if filtered_pkgs and not _pkg_tree_contains(pm, pkg, filtered_pkgs):
            continue
        printed_pkgs = pm.memcache_get("__printed_pkgs", [])
        if printed_pkgs and pkg.path in printed_pkgs:
            continue
        printed_pkgs.append(pkg.path)
        pm.memcache_set("__printed_pkgs", printed_pkgs)

        click.echo(
            "%s%s %s"
            % (
                "│   " * level,
                "├──" if index < len(candidates) - 1 else "└──",
                humanize_package(
                    pkg,
                    spec=spec,
                    verbose=verbose,
                ),
            )
        )

        dependencies = pm.get_pkg_dependencies(pkg)
        if dependencies:
            print_dependency_tree(
                pm,
                specs=[pm.dependency_to_spec(item) for item in dependencies],
                filter_specs=filter_specs,
                level=level + 1,
                verbose=verbose,
            )


def _pkg_tree_contains(pm, root: PackageItem, children: List[PackageItem]):
    if root in children:
        return True
    for dependency in pm.get_pkg_dependencies(root) or []:
        pkg = pm.get_package(pm.dependency_to_spec(dependency))
        if pkg and _pkg_tree_contains(pm, pkg, children):
            return True
    return False


def list_global_packages(options):
    data = [
        ("platforms", PlatformPackageManager(options.get("storage_dir"))),
        ("tools", ToolPackageManager(options.get("storage_dir"))),
        ("libraries", LibraryPackageManager(options.get("storage_dir"))),
    ]
    only_packages = any(
        options.get(typex) or options.get(f"only_{typex}") for (typex, _) in data
    )
    for typex, pm in data:
        skip_conds = [
            only_packages
            and not options.get(typex)
            and not options.get(f"only_{typex}"),
            not pm.get_installed(),
        ]
        if any(skip_conds):
            continue
        click.secho(typex.capitalize(), bold=True)
        print_dependency_tree(
            pm, filter_specs=options.get(typex), verbose=options.get("verbose")
        )
        click.echo()


def list_project_packages(options):
    environments = options["environments"]
    only_packages = any(
        options.get(typex) or options.get(f"only_{typex}")
        for typex in ("platforms", "tools", "libraries")
    )
    only_platform_packages = any(
        options.get(typex) or options.get(f"only_{typex}")
        for typex in ("platforms", "tools")
    )
    only_library_packages = options.get("libraries") or options.get("only_libraries")

    with fs.cd(options["project_dir"]):
        config = ProjectConfig.get_instance()
        config.validate(environments)
        for env in config.envs():
            if environments and env not in environments:
                continue
            click.echo("Resolving %s dependencies..." % click.style(env, fg="cyan"))
            found = False
            if not only_packages or only_platform_packages:
                _found = print_project_env_platform_packages(env, options)
                found = found or _found
            if not only_packages or only_library_packages:
                _found = print_project_env_library_packages(env, options)
                found = found or _found
            if not found:
                click.echo("No packages")
            if (not environments and len(config.envs()) > 1) or len(environments) > 1:
                click.echo()


def print_project_env_platform_packages(project_env, options):
    try:
        p = PlatformFactory.from_env(project_env)
    except UnknownPlatform:
        return None
    click.echo(
        "Platform %s"
        % (
            humanize_package(
                PlatformPackageManager().get_package(p.get_dir()),
                p.config.get(f"env:{project_env}", "platform"),
                verbose=options.get("verbose"),
            )
        )
    )
    print_dependency_tree(
        p.pm,
        specs=[p.get_package_spec(name) for name in p.packages],
        filter_specs=options.get("tools"),
    )
    click.echo()
    return True


def print_project_env_library_packages(project_env, options):
    config = ProjectConfig.get_instance()
    lib_deps = config.get(f"env:{project_env}", "lib_deps")
    lm = LibraryPackageManager(
        os.path.join(config.get("superide", "libdeps_dir"), project_env)
    )
    if not lib_deps or not lm.get_installed():
        return None
    click.echo("Libraries")
    print_dependency_tree(
        lm,
        lib_deps,
        filter_specs=options.get("libraries"),
        verbose=options.get("verbose"),
    )
    return True
