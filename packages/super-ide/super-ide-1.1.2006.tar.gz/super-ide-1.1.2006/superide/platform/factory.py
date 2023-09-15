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
import re
import sys

from superide import fs
from superide.compat import load_python_module
from superide.package.meta import PackageItem
from superide.platform import base
from superide.platform.exception import UnknownPlatform
from superide.project.config import ProjectConfig
from superide.project.exception import UndefinedEnvPlatformError


class PlatformFactory:
    @staticmethod
    def get_clsname(name):
        name = re.sub(r"[^\da-z\_]+", "", name, flags=re.I)
        return "%sPlatform" % name.lower().capitalize()

    @staticmethod
    def load_platform_module(name, path):
        # backward compatibiility with the legacy dev-platforms
        sys.modules["superide.managers.platform"] = base
        try:
            return load_python_module("superide.platform.%s" % name, path)
        except ImportError as exc:
            raise UnknownPlatform(name) from exc

    @classmethod
    def new(cls, pkg_or_spec, autoinstall=False) -> base.PlatformBase:
        # pylint: disable=import-outside-toplevel
        from superide.package.manager.platform import PlatformPackageManager

        platform_dir = None
        platform_name = None
        if isinstance(pkg_or_spec, PackageItem):
            platform_dir = pkg_or_spec.path
            platform_name = pkg_or_spec.metadata.name
        elif isinstance(pkg_or_spec, (str, bytes)) and os.path.isdir(pkg_or_spec):
            platform_dir = pkg_or_spec
        else:
            pkg = PlatformPackageManager().get_package(pkg_or_spec)
            if pkg:
                platform_dir = pkg.path
                platform_name = pkg.metadata.name

        if not platform_dir or not os.path.isfile(
            os.path.join(platform_dir, "platform.json")
        ):
            if autoinstall:
                return cls.new(
                    PlatformPackageManager().install(
                        pkg_or_spec, skip_dependencies=True
                    )
                )
            raise UnknownPlatform(pkg_or_spec)

        if not platform_name:
            platform_name = fs.load_json(os.path.join(platform_dir, "platform.json"))[
                "name"
            ]

        platform_cls = None
        if os.path.isfile(os.path.join(platform_dir, "platform.py")):
            platform_cls = getattr(
                cls.load_platform_module(
                    platform_name, os.path.join(platform_dir, "platform.py")
                ),
                cls.get_clsname(platform_name),
            )
        else:
            platform_cls = type(
                str(cls.get_clsname(platform_name)), (base.PlatformBase,), {}
            )

        _instance = platform_cls(os.path.join(platform_dir, "platform.json"))
        assert isinstance(_instance, base.PlatformBase)
        return _instance

    @classmethod
    def from_env(cls, env, targets=None, autoinstall=False):
        config = ProjectConfig.get_instance()
        spec = config.get(f"env:{env}", "platform", None)
        if not spec:
            raise UndefinedEnvPlatformError(env)
        p = cls.new(spec, autoinstall=autoinstall)
        p.project_env = env
        p.configure_project_packages(env, targets)
        return p
