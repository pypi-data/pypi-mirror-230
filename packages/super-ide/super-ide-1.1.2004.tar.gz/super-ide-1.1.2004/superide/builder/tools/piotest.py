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

from superide.builder.tools import piobuild
from superide.test.result import TestSuite
from superide.test.runners.factory import TestRunnerFactory


def ConfigureTestTarget(env):
    env.Append(
        CPPDEFINES=["UNIT_TEST"],  # deprecated, use PIO_UNIT_TESTING
        PIOTEST_SRC_FILTER=[f"+<*.{ext}>" for ext in piobuild.SRC_BUILD_EXT],
    )
    env.Prepend(CPPPATH=["$PROJECT_TEST_DIR"])

    if "PIOTEST_RUNNING_NAME" in env:
        test_name = env["PIOTEST_RUNNING_NAME"]
        while True:
            test_name = os.path.dirname(test_name)  # parent dir
            # skip nested tests (user's side issue?)
            if not test_name or os.path.basename(test_name).startswith("test_"):
                break
            env.Prepend(
                PIOTEST_SRC_FILTER=[
                    f"+<{test_name}{os.path.sep}*.{ext}>"
                    for ext in piobuild.SRC_BUILD_EXT
                ],
                CPPPATH=[os.path.join("$PROJECT_TEST_DIR", test_name)],
            )

        env.Prepend(
            PIOTEST_SRC_FILTER=[f"+<$PIOTEST_RUNNING_NAME{os.path.sep}>"],
            CPPPATH=[os.path.join("$PROJECT_TEST_DIR", "$PIOTEST_RUNNING_NAME")],
        )

    test_runner = TestRunnerFactory.new(
        TestSuite(env["PIOENV"], env.get("PIOTEST_RUNNING_NAME", "*")),
        env.GetProjectConfig(),
    )
    test_runner.configure_build_env(env)


def generate(env):
    env.AddMethod(ConfigureTestTarget)


def exists(_):
    return True
