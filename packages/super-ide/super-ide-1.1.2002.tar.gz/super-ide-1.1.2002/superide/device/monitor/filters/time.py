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

from datetime import datetime

from superide.device.monitor.filters.base import DeviceMonitorFilterBase


class Timestamp(DeviceMonitorFilterBase):
    NAME = "time"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._line_started = False

    def rx(self, text):
        if self._line_started and "\n" not in text:
            return text
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        if not self._line_started:
            self._line_started = True
            text = "%s > %s" % (timestamp, text)
        if text.endswith("\n"):
            self._line_started = False
            return text[:-1].replace("\n", "\n%s > " % timestamp) + "\n"
        return text.replace("\n", "\n%s > " % timestamp)
