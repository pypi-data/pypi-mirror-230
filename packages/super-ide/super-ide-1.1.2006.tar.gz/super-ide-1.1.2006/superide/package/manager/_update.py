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

import click

from superide.package.exception import UnknownPackageError
from superide.package.meta import PackageItem, PackageOutdatedResult, PackageSpec
from superide.package.vcsclient import VCSBaseException, VCSClientFactory


class PackageManagerUpdateMixin:
    def outdated(self, pkg, spec=None):
        assert isinstance(pkg, PackageItem)
        assert pkg.metadata

        if spec and not isinstance(spec, PackageSpec):
            spec = PackageSpec(spec)

        if not os.path.isdir(pkg.path):
            return PackageOutdatedResult(current=pkg.metadata.version)

        # skip detached package to a specific version
        detached_conditions = [
            "@" in pkg.path,
            pkg.metadata.spec and not pkg.metadata.spec.external,
            not spec,
        ]
        if all(detached_conditions):
            return PackageOutdatedResult(current=pkg.metadata.version, detached=True)

        latest = None
        wanted = None
        if pkg.metadata.spec.external:
            latest = self._fetch_vcs_latest_version(pkg)
        else:
            try:
                reg_pkg = self.fetch_registry_package(pkg.metadata.spec)
                latest = (
                    self.pick_best_registry_version(reg_pkg["versions"]) or {}
                ).get("name")
                if spec:
                    wanted = (
                        self.pick_best_registry_version(reg_pkg["versions"], spec) or {}
                    ).get("name")
                    if not wanted:  # wrong library
                        latest = None
            except UnknownPackageError:
                pass

        return PackageOutdatedResult(
            current=pkg.metadata.version, latest=latest, wanted=wanted
        )

    def _fetch_vcs_latest_version(self, pkg):
        vcs = None
        try:
            vcs = VCSClientFactory.new(pkg.path, pkg.metadata.spec.uri, silent=True)
        except VCSBaseException:
            return None
        if not vcs.can_be_updated:
            return None

        vcs_revision = vcs.get_latest_revision()
        if not vcs_revision:
            return None

        return str(
            self.build_metadata(
                pkg.path, pkg.metadata.spec, vcs_revision=vcs_revision
            ).version
        )

    def update(
        self,
        from_spec,
        to_spec=None,
        skip_dependencies=False,
    ):
        pkg = self.get_package(from_spec)
        if not pkg or not pkg.metadata:
            raise UnknownPackageError(from_spec)

        outdated = self.outdated(pkg, to_spec)
        if not outdated.is_outdated(allow_incompatible=False):
            self.log.debug(
                click.style(
                    "{name}@{version} is already up-to-date".format(
                        **pkg.metadata.as_dict()
                    ),
                    fg="yellow",
                )
            )
            return pkg

        self.log.info(
            "Updating %s @ %s"
            % (click.style(pkg.metadata.name, fg="cyan"), pkg.metadata.version)
        )
        try:
            self.lock()
            return self._update(pkg, outdated, skip_dependencies)
        finally:
            self.unlock()

    def _update(self, pkg, outdated, skip_dependencies=False):
        if pkg.metadata.spec.external:
            vcs = VCSClientFactory.new(pkg.path, pkg.metadata.spec.uri)
            assert vcs.update()
            pkg.metadata.version = self._fetch_vcs_latest_version(pkg)
            pkg.dump_meta()
            return pkg

        # uninstall existing version
        self.uninstall(pkg, skip_dependencies=True)

        return self.install(
            PackageSpec(
                id=pkg.metadata.spec.id,
                owner=pkg.metadata.spec.owner,
                name=pkg.metadata.spec.name,
                requirements=outdated.wanted or outdated.latest,
            ),
            skip_dependencies=skip_dependencies,
        )
