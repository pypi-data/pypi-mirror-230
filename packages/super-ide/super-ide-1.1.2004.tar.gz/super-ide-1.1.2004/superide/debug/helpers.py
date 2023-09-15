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
import re
import sys
import time
from hashlib import sha1
from io import BytesIO

from superide.cli import PlatformioCLI
from superide.compat import is_bytes
from superide.debug.exception import DebugInvalidOptionsError
from superide.run.cli import cli as cmd_run
from superide.run.cli import print_processing_header
from superide.test.helpers import list_test_names
from superide.test.result import TestSuite
from superide.test.runners.base import TestRunnerOptions
from superide.test.runners.factory import TestRunnerFactory


class GDBMIConsoleStream(BytesIO):  # pylint: disable=too-few-public-methods
    STDOUT = sys.stdout

    def write(self, text):
        self.STDOUT.write(escape_gdbmi_stream("~", text))
        self.STDOUT.flush()


def is_gdbmi_mode():
    return "--interpreter" in " ".join(PlatformioCLI.leftover_args)


def escape_gdbmi_stream(prefix, stream):
    bytes_stream = False
    if is_bytes(stream):
        bytes_stream = True
        stream = stream.decode()

    if not stream:
        return b"" if bytes_stream else ""

    ends_nl = stream.endswith("\n")
    stream = re.sub(r"\\+", "\\\\\\\\", stream)
    stream = stream.replace('"', '\\"')
    stream = stream.replace("\n", "\\n")
    stream = '%s"%s"' % (prefix, stream)
    if ends_nl:
        stream += "\n"

    return stream.encode() if bytes_stream else stream


def get_default_debug_env(config):
    default_envs = config.default_envs()
    all_envs = config.envs()
    for env in default_envs:
        if config.get("env:" + env, "build_type") == "debug":
            return env
    for env in all_envs:
        if config.get("env:" + env, "build_type") == "debug":
            return env
    return default_envs[0] if default_envs else all_envs[0]


def predebug_project(
    ctx, project_dir, project_config, env_name, preload, verbose
):  # pylint: disable=too-many-arguments
    debug_testname = project_config.get("env:" + env_name, "debug_test")
    if debug_testname:
        test_names = list_test_names(project_config)
        if debug_testname not in test_names:
            raise DebugInvalidOptionsError(
                "Unknown test name `%s`. Valid names are `%s`"
                % (debug_testname, ", ".join(test_names))
            )
        print_processing_header(env_name, project_config, verbose)
        test_runner = TestRunnerFactory.new(
            TestSuite(env_name, debug_testname),
            project_config,
            TestRunnerOptions(
                verbose=3 if verbose else 0,
                without_building=False,
                without_debugging=False,
                without_uploading=not preload,
                without_testing=True,
            ),
        )
        test_runner.start(ctx)
    else:
        ctx.invoke(
            cmd_run,
            project_dir=project_dir,
            project_conf=project_config.path,
            environment=[env_name],
            target=["__debug"] + (["upload"] if preload else []),
            verbose=verbose,
        )

    if preload:
        time.sleep(5)


def has_debug_symbols(prog_path):
    if not os.path.isfile(prog_path):
        return False
    matched = {
        b".debug_info": False,
        b".debug_abbrev": False,
        b" -Og": False,
        b" -g": False,
        # b"__PLATFORMIO_BUILD_DEBUG__": False,
    }
    with open(prog_path, "rb") as fp:
        last_data = b""
        while True:
            data = fp.read(1024)
            if not data:
                break
            for pattern, found in matched.items():
                if found:
                    continue
                if pattern in last_data + data:
                    matched[pattern] = True
            last_data = data
    return all(matched.values())


def is_prog_obsolete(prog_path):
    prog_hash_path = prog_path + ".sha1"
    if not os.path.isfile(prog_path):
        return True
    shasum = sha1()
    with open(prog_path, "rb") as fp:
        while True:
            data = fp.read(1024)
            if not data:
                break
            shasum.update(data)
    new_digest = shasum.hexdigest()
    old_digest = None
    if os.path.isfile(prog_hash_path):
        with open(prog_hash_path, encoding="utf8") as fp:
            old_digest = fp.read()
    if new_digest == old_digest:
        return False
    with open(prog_hash_path, mode="w", encoding="utf8") as fp:
        fp.write(new_digest)
    return True
