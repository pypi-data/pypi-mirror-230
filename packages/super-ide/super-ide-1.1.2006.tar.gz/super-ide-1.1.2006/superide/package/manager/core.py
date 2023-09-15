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

from superide import __core_packages__, exception
from superide.package.exception import UnknownPackageError
from superide.package.manager.tool import ToolPackageManager
from superide.package.meta import PackageSpec


def get_installed_core_packages():
    result = []
    pm = ToolPackageManager()
    for name, requirements in __core_packages__.items():
        spec = PackageSpec(owner="superide", name=name, requirements=requirements)
        pkg = pm.get_package(spec)
        if pkg:
            result.append(pkg)
    return result


def get_core_package_dir(name, spec=None, auto_install=True):
    if name not in __core_packages__:
        raise exception.PlatformioException("Please upgrade superide Core")
    pm = ToolPackageManager()
    spec = spec or PackageSpec(
        owner="superide", name=name, requirements=__core_packages__[name]
    )
    pkg = pm.get_package(spec)
    if pkg:
        return pkg.path
    if not auto_install:
        return None
    assert pm.install(spec)
    remove_unnecessary_core_packages()
    return pm.get_package(spec).path


def update_core_packages():
    pm = ToolPackageManager()
    for name, requirements in __core_packages__.items():
        spec = PackageSpec(owner="superide", name=name, requirements=requirements)
        try:
            pm.update(spec, spec)
        except UnknownPackageError:
            pass
    remove_unnecessary_core_packages()
    return True


def remove_unnecessary_core_packages(dry_run=False):
    candidates = []
    pm = ToolPackageManager()
    best_pkg_versions = {}

    for name, requirements in __core_packages__.items():
        spec = PackageSpec(owner="superide", name=name, requirements=requirements)
        pkg = pm.get_package(spec)
        if not pkg:
            continue
        # pylint: disable=no-member
        best_pkg_versions[pkg.metadata.name] = pkg.metadata.version

    for pkg in pm.get_installed():
        skip_conds = [
            os.path.isfile(os.path.join(pkg.path, ".piokeep")),
            pkg.metadata.spec.owner != "superide",
            pkg.metadata.name not in best_pkg_versions,
            pkg.metadata.name in best_pkg_versions
            and pkg.metadata.version == best_pkg_versions[pkg.metadata.name],
        ]
        if not any(skip_conds):
            candidates.append(pkg)

    if dry_run:
        return candidates

    for pkg in candidates:
        pm.uninstall(pkg)

    return candidates
