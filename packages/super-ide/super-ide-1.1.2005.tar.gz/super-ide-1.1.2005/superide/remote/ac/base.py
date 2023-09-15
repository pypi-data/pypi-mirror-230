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

from twisted.internet import defer  # pylint: disable=import-error
from twisted.spread import pb  # pylint: disable=import-error


class AsyncCommandBase:
    MAX_BUFFER_SIZE = 1024 * 1024  # 1Mb

    def __init__(self, options=None, on_end_callback=None):
        self.options = options or {}
        self.on_end_callback = on_end_callback
        self._buffer = b""
        self._return_code = None
        self._d = None
        self._paused = False

        try:
            self.start()
        except Exception as exc:
            raise pb.Error(str(exc)) from exc

    @property
    def id(self):
        return id(self)

    def pause(self):
        self._paused = True
        self.stop()

    def unpause(self):
        self._paused = False
        self.start()

    def start(self):
        raise NotImplementedError

    def stop(self):
        self.transport.loseConnection()  # pylint: disable=no-member

    def _ac_ended(self):
        if self.on_end_callback:
            self.on_end_callback()
        if not self._d or self._d.called:
            self._d = None
            return
        if self._buffer:
            self._d.callback(self._buffer)
        else:
            self._d.callback(None)

    def _ac_ondata(self, data):
        self._buffer += data
        if len(self._buffer) > self.MAX_BUFFER_SIZE:
            self._buffer = self._buffer[-1 * self.MAX_BUFFER_SIZE :]
        if self._paused:
            return
        if self._d and not self._d.called:
            self._d.callback(self._buffer)
            self._buffer = b""

    def ac_read(self):
        if self._buffer:
            result = self._buffer
            self._buffer = b""
            return result
        if self._return_code is None:
            self._d = defer.Deferred()
            return self._d
        return None

    def ac_write(self, data):
        self.transport.write(data)  # pylint: disable=no-member
        return len(data)

    def ac_close(self):
        self.stop()
        return self._return_code
