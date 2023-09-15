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

from superide.device.monitor.filters.base import DeviceMonitorFilterBase


class SendOnEnter(DeviceMonitorFilterBase):
    NAME = "send_on_enter"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._buffer = ""

        if self.options.get("eol") == "CR":
            self._eol = "\r"
        elif self.options.get("eol") == "LF":
            self._eol = "\n"
        else:
            self._eol = "\r\n"

    def tx(self, text):
        self._buffer += text
        if self._buffer.endswith(self._eol):
            text = self._buffer
            self._buffer = ""
            return text
        return ""
