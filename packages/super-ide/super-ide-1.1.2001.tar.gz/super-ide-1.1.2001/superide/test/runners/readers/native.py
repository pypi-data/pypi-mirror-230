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

import asyncio
import os
import signal
import subprocess
import time

from superide.compat import (
    IS_WINDOWS,
    aio_get_running_loop,
    get_filesystem_encoding,
    get_locale_encoding,
)
from superide.project.helpers import load_build_metadata
from superide.test.exception import UnitTestError

EXITING_TIMEOUT = 5  # seconds


class ProgramProcessProtocol(asyncio.SubprocessProtocol):
    def __init__(self, test_runner, exit_future):
        self.test_runner = test_runner
        self.exit_future = exit_future
        self._exit_timer = None

    def pipe_data_received(self, _, data):
        try:
            data = data.decode(get_locale_encoding() or get_filesystem_encoding())
        except UnicodeDecodeError:
            data = data.decode("latin-1")
        self.test_runner.on_testing_data_output(data)
        if self.test_runner.test_suite.is_finished():
            self._exit_timer = aio_get_running_loop().call_later(
                EXITING_TIMEOUT, self._stop_testing
            )

    def process_exited(self):
        self._stop_testing()

    def _stop_testing(self):
        if not self.exit_future.done():
            self.exit_future.set_result(True)
        if self._exit_timer:
            self._exit_timer.cancel()


class NativeTestOutputReader:
    def __init__(self, test_runner):
        self.test_runner = test_runner
        self.aio_loop = (
            asyncio.ProactorEventLoop() if IS_WINDOWS else asyncio.new_event_loop()
        )
        asyncio.set_event_loop(self.aio_loop)

    def get_testing_command(self):
        custom_testing_command = self.test_runner.project_config.get(
            f"env:{self.test_runner.test_suite.env_name}", "test_testing_command"
        )
        if custom_testing_command:
            return custom_testing_command
        build_dir = self.test_runner.project_config.get("superide", "build_dir")
        cmd = [
            os.path.join(
                build_dir,
                self.test_runner.test_suite.env_name,
                "program.exe" if IS_WINDOWS else "program",
            )
        ]
        # if user changed PROGNAME
        if not os.path.exists(cmd[0]):
            build_data = load_build_metadata(
                os.getcwd(), self.test_runner.test_suite.env_name, cache=True
            )
            if build_data:
                cmd[0] = build_data["prog_path"]
        if self.test_runner.options.program_args:
            cmd.extend(self.test_runner.options.program_args)
        return cmd

    async def gather_results(self):
        exit_future = asyncio.Future(loop=self.aio_loop)
        transport, _ = await self.aio_loop.subprocess_exec(
            lambda: ProgramProcessProtocol(self.test_runner, exit_future),
            *self.get_testing_command(),
            stdin=None,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        await exit_future
        last_return_code = transport.get_returncode()
        transport.close()

        # wait until subprocess will be killed
        start = time.time()
        while (
            start > (time.time() - EXITING_TIMEOUT)
            and transport.get_returncode() is None
        ):
            await asyncio.sleep(0.5)

        if last_return_code:
            self.raise_for_status(last_return_code)

    @staticmethod
    def raise_for_status(return_code):
        try:
            sig = signal.Signals(abs(return_code))
            try:
                signal_description = signal.strsignal(sig)
            except AttributeError:
                signal_description = ""
            raise UnitTestError(
                f"Program received signal {sig.name} ({signal_description})"
            )
        except ValueError as exc:
            raise UnitTestError("Program errored with %d code" % return_code) from exc

    def begin(self):
        try:
            self.aio_loop.run_until_complete(self.gather_results())
        finally:
            self.aio_loop.run_until_complete(self.aio_loop.shutdown_asyncgens())
            self.aio_loop.close()
