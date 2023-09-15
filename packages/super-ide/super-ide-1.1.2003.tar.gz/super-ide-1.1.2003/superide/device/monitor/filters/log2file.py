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

import io
import os
from datetime import datetime

from superide.device.monitor.filters.base import DeviceMonitorFilterBase


class LogToFile(DeviceMonitorFilterBase):
    NAME = "log2file"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._log_fp = None

    def __call__(self):
        if not os.path.isdir("logs"):
            os.makedirs("logs")
        log_file_name = os.path.join(
            "logs", "device-monitor-%s.log" % datetime.now().strftime("%y%m%d-%H%M%S")
        )
        print("--- Logging an output to %s" % os.path.abspath(log_file_name))
        # pylint: disable=consider-using-with
        self._log_fp = io.open(log_file_name, "w", encoding="utf-8")
        return self

    def __del__(self):
        if self._log_fp:
            self._log_fp.close()

    def rx(self, text):
        self._log_fp.write(text)
        self._log_fp.flush()
        return text
