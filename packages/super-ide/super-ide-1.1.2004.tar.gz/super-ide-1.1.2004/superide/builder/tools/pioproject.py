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

from superide.compat import MISSING
from superide.project.config import ProjectConfig


def GetProjectConfig(env):
    return ProjectConfig.get_instance(env["PROJECT_CONFIG"])


def GetProjectOptions(env, as_dict=False):
    return env.GetProjectConfig().items(env=env["PIOENV"], as_dict=as_dict)


def GetProjectOption(env, option, default=MISSING):
    return env.GetProjectConfig().get("env:" + env["PIOENV"], option, default)


def LoadProjectOptions(env):
    config = env.GetProjectConfig()
    section = "env:" + env["PIOENV"]
    for option in config.options(section):
        option_meta = config.find_option_meta(section, option)
        if (
            not option_meta
            or not option_meta.buildenvvar
            or option_meta.buildenvvar in env
        ):
            continue
        env[option_meta.buildenvvar] = config.get(section, option)


def exists(_):
    return True


def generate(env):
    env.AddMethod(GetProjectConfig)
    env.AddMethod(GetProjectOptions)
    env.AddMethod(GetProjectOption)
    env.AddMethod(LoadProjectOptions)
    return env
