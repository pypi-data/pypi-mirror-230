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

import importlib
import os
import re

from superide.compat import load_python_module
from superide.exception import UserSideException
from superide.project.config import ProjectConfig
from superide.test.result import TestSuite
from superide.test.runners.base import TestRunnerBase, TestRunnerOptions


class TestRunnerFactory:
    @staticmethod
    def get_clsname(name):
        name = re.sub(r"[^\da-z\_\-]+", "", name, flags=re.I)
        return "%sTestRunner" % name.lower().capitalize()

    @classmethod
    def new(cls, test_suite, project_config, options=None) -> TestRunnerBase:
        assert isinstance(test_suite, TestSuite)
        assert isinstance(project_config, ProjectConfig)
        if options:
            assert isinstance(options, TestRunnerOptions)
        test_framework = project_config.get(
            f"env:{test_suite.env_name}", "test_framework"
        )
        module_name = f"superide.test.runners.{test_framework}"
        runner_cls = None
        if test_framework == "custom":
            test_dir = project_config.get("superide", "test_dir")
            custom_runner_path = os.path.join(test_dir, "test_custom_runner.py")
            test_name = test_suite.test_name if test_suite.test_name != "*" else None
            while test_name:
                if os.path.isfile(
                    os.path.join(test_dir, test_name, "test_custom_runner.py")
                ):
                    custom_runner_path = os.path.join(
                        test_dir, test_name, "test_custom_runner.py"
                    )
                    break
                test_name = os.path.dirname(test_name)  # parent dir

            try:
                mod = load_python_module(module_name, custom_runner_path)
            except (FileNotFoundError, ImportError) as exc:
                raise UserSideException(
                    "Could not find custom test runner "
                    f"by this path -> {custom_runner_path}"
                ) from exc
        else:
            mod = importlib.import_module(module_name)
        runner_cls = getattr(mod, cls.get_clsname(test_framework))
        return runner_cls(test_suite, project_config, options)
