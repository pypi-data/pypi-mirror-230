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

from superide.package.commands.install import install_project_env_dependencies
from superide.platform.factory import PlatformFactory
from superide.project.exception import UndefinedEnvPlatformError
from superide.run.helpers import KNOWN_ALLCLEAN_TARGETS
from superide.test.runners.base import CTX_META_TEST_RUNNING_NAME

# pylint: disable=too-many-instance-attributes


class EnvironmentProcessor:
    def __init__(  # pylint: disable=too-many-arguments
        self,
        cmd_ctx,
        name,
        config,
        targets,
        upload_port,
        jobs,
        program_args,
        silent,
        verbose,
    ):
        self.cmd_ctx = cmd_ctx
        self.name = name
        self.config = config
        self.targets = targets
        self.upload_port = upload_port
        self.jobs = jobs
        self.program_args = program_args
        self.silent = silent
        self.verbose = verbose
        self.options = config.items(env=name, as_dict=True)

    def get_build_variables(self):
        variables = dict(
            pioenv=self.name,
            project_config=self.config.path,
            program_args=self.program_args,
        )

        if CTX_META_TEST_RUNNING_NAME in self.cmd_ctx.meta:
            variables["piotest_running_name"] = self.cmd_ctx.meta[
                CTX_META_TEST_RUNNING_NAME
            ]

        if self.upload_port:
            # override upload port with a custom from CLI
            variables["upload_port"] = self.upload_port
        return variables

    def process(self):
        if "platform" not in self.options:
            raise UndefinedEnvPlatformError(self.name)

        build_vars = self.get_build_variables()
        is_clean = set(KNOWN_ALLCLEAN_TARGETS) & set(self.targets)
        build_targets = [t for t in self.targets if t not in KNOWN_ALLCLEAN_TARGETS]

        # pre-clean
        if is_clean:
            result = PlatformFactory.from_env(
                self.name, targets=self.targets, autoinstall=True
            ).run(build_vars, self.targets, self.silent, self.verbose, self.jobs)
            if not build_targets:
                return result["returncode"] == 0

        install_project_env_dependencies(
            self.name,
            {
                "project_targets": self.targets,
                "piotest_running_name": build_vars.get("piotest_running_name"),
            },
        )
        result = PlatformFactory.from_env(
            self.name, targets=build_targets, autoinstall=True
        ).run(build_vars, build_targets, self.silent, self.verbose, self.jobs)
        return result["returncode"] == 0
