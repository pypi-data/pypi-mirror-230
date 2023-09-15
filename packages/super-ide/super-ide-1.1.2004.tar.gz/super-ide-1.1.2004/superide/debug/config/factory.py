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
import re

from superide.debug.config.generic import GenericDebugConfig
from superide.debug.config.native import NativeDebugConfig


class DebugConfigFactory:
    @staticmethod
    def get_clsname(name):
        name = re.sub(r"[^\da-z\_\-]+", "", name, flags=re.I)
        return "%sDebugConfig" % name.lower().capitalize()

    @classmethod
    def new(cls, platform, project_config, env_name):
        board_config = platform.board_config(
            project_config.get("env:" + env_name, "board")
        )
        tool_name = (
            board_config.get_debug_tool_name(
                project_config.get("env:" + env_name, "debug_tool")
            )
            if board_config
            else None
        )
        config_cls = None
        try:
            mod = importlib.import_module("superide.debug.config.%s" % tool_name)
            config_cls = getattr(mod, cls.get_clsname(tool_name))
        except ModuleNotFoundError:
            config_cls = (
                GenericDebugConfig if platform.is_embedded() else NativeDebugConfig
            )
        return config_cls(platform, project_config, env_name)
