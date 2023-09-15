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

from superide.package.meta import PackageSpec


class PlatformPackagesMixin:
    def get_package_spec(self, name, version=None):
        return PackageSpec(
            owner=self.packages[name].get("owner"),
            name=name,
            requirements=version or self.packages[name].get("version"),
        )

    def get_package(self, name, spec=None):
        if not name:
            return None
        return self.pm.get_package(spec or self.get_package_spec(name))

    def get_package_dir(self, name):
        pkg = self.get_package(name)
        return pkg.path if pkg else None

    def get_package_version(self, name):
        pkg = self.get_package(name)
        return str(pkg.metadata.version) if pkg else None

    def get_installed_packages(self, with_optional=True, with_optional_versions=False):
        result = []
        for name, options in dict(sorted(self.packages.items())).items():
            if not with_optional and options.get("optional"):
                continue
            versions = [options.get("version")]
            if with_optional_versions:
                versions.extend(options.get("optionalVersions", []))
            for version in versions:
                if not version:
                    continue
                pkg = self.get_package(name, self.get_package_spec(name, version))
                if pkg:
                    result.append(pkg)
        return result

    def dump_used_packages(self):
        result = []
        for name, options in self.packages.items():
            if options.get("optional"):
                continue
            pkg = self.get_package(name)
            if not pkg or not pkg.metadata:
                continue
            item = {"name": pkg.metadata.name, "version": str(pkg.metadata.version)}
            if pkg.metadata.spec.external:
                item["src_url"] = pkg.metadata.spec.uri
            result.append(item)
        return result

    def install_package(self, name, spec=None, force=False):
        return self.pm.install(spec or self.get_package_spec(name), force=force)

    def install_required_packages(self, force=False):
        for name, options in self.packages.items():
            if options.get("optional"):
                continue
            self.install_package(name, force=force)

    def uninstall_packages(self):
        for pkg in self.get_installed_packages():
            self.pm.uninstall(pkg)

    def update_packages(self):
        for pkg in self.get_installed_packages():
            self.pm.update(pkg, to_spec=self.get_package_spec(pkg.metadata.name))

    def are_outdated_packages(self):
        for pkg in self.get_installed_packages():
            if self.pm.outdated(
                pkg, self.get_package_spec(pkg.metadata.name)
            ).is_outdated(allow_incompatible=False):
                return True
        return False
