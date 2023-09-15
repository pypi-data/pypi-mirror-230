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

import serial

from superide.device.monitor.filters.base import DeviceMonitorFilterBase


class Hexlify(DeviceMonitorFilterBase):
    NAME = "hexlify"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._counter = 0

    def rx(self, text):
        result = ""
        for b in serial.iterbytes(text):
            if (self._counter % 16) == 0:
                result += "\n{:04X} | ".format(self._counter)
            asciicode = ord(b)
            if asciicode <= 255:
                result += "{:02X} ".format(asciicode)
            else:
                result += "?? "
            self._counter += 1
        return result
