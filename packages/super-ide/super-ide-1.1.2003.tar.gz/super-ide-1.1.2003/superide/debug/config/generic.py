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

from superide.debug.config.base import DebugConfigBase


class GenericDebugConfig(DebugConfigBase):
    GDB_INIT_SCRIPT = """
define pio_reset_halt_target
    monitor reset halt
end

define pio_reset_run_target
    monitor reset
end

target extended-remote $DEBUG_PORT
monitor init
$LOAD_CMDS
pio_reset_halt_target
$INIT_BREAK
"""

    def __init__(self, *args, **kwargs):
        if "port" not in kwargs:
            kwargs["port"] = ":3333"
        super().__init__(*args, **kwargs)
