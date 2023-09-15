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
from fnmatch import fnmatch

from superide.test.exception import TestDirNotExistsError
from superide.test.result import TestSuite


def list_test_names(project_config):
    test_dir = project_config.get("superide", "test_dir")
    if not os.path.isdir(test_dir):
        raise TestDirNotExistsError(test_dir)
    names = []
    for root, _, __ in os.walk(test_dir, followlinks=True):
        if not os.path.basename(root).startswith("test_"):
            continue
        names.append(os.path.relpath(root, test_dir).replace("\\", "/"))
    if not names:
        names = ["*"]
    return names


def list_test_suites(project_config, environments, filters, ignores):
    result = []
    test_dir = project_config.get("superide", "test_dir")
    default_envs = project_config.default_envs()
    test_names = list_test_names(project_config)
    for env_name in project_config.envs():
        for test_name in test_names:
            # filter and ignore patterns
            patterns = dict(filter=list(filters), ignore=list(ignores))
            for key, value in patterns.items():
                if value:  # overridden from CLI
                    continue
                patterns[key].extend(  # pylint: disable=unnecessary-dict-index-lookup
                    project_config.get(f"env:{env_name}", f"test_{key}", [])
                )

            skip_conditions = [
                environments and env_name not in environments,
                not environments and default_envs and env_name not in default_envs,
                test_name != "*"
                and patterns["filter"]
                and not any(fnmatch(test_name, p) for p in patterns["filter"]),
                test_name != "*"
                and any(fnmatch(test_name, p) for p in patterns["ignore"]),
            ]
            result.append(
                TestSuite(
                    env_name,
                    test_name,
                    finished=any(skip_conditions),
                    test_dir=os.path.abspath(
                        test_dir
                        if test_name == "*"
                        else os.path.join(test_dir, test_name)
                    ),
                )
            )
    return result
