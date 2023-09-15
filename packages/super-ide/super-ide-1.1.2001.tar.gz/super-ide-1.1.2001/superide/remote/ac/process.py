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

from twisted.internet import protocol, reactor  # pylint: disable=import-error

from superide.remote.ac.base import AsyncCommandBase


class ProcessAsyncCmd(protocol.ProcessProtocol, AsyncCommandBase):
    def start(self):
        env = dict(os.environ).copy()
        env.update({"PLATFORMIO_FORCE_ANSI": "true"})
        reactor.spawnProcess(
            self, self.options["executable"], self.options["args"], env
        )

    def outReceived(self, data):
        self._ac_ondata(data)

    def errReceived(self, data):
        self._ac_ondata(data)

    def processExited(self, reason):
        self._return_code = reason.value.exitCode

    def processEnded(self, reason):
        if self._return_code is None:
            self._return_code = reason.value.exitCode
        self._ac_ended()
