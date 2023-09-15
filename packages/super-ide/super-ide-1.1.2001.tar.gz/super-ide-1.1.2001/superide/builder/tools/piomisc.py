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
import sys

from superide import fs, util
from superide.proc import exec_command


@util.memoized()
def GetCompilerType(env):
    if env.subst("$CC").endswith("-gcc"):
        return "gcc"
    try:
        sysenv = os.environ.copy()
        sysenv["PATH"] = str(env["ENV"]["PATH"])
        result = exec_command([env.subst("$CC"), "-v"], env=sysenv)
    except OSError:
        return None
    if result["returncode"] != 0:
        return None
    output = "".join([result["out"], result["err"]]).lower()
    if "clang" in output and "LLVM" in output:
        return "clang"
    if "gcc" in output:
        return "gcc"
    return None


def GetActualLDScript(env):
    def _lookup_in_ldpath(script):
        for d in env.get("LIBPATH", []):
            path = os.path.join(env.subst(d), script)
            if os.path.isfile(path):
                return path
        return None

    script = None
    script_in_next = False
    for f in env.get("LINKFLAGS", []):
        raw_script = None
        if f == "-T":
            script_in_next = True
            continue
        if script_in_next:
            script_in_next = False
            raw_script = f
        elif f.startswith("-Wl,-T"):
            raw_script = f[6:]
        else:
            continue
        script = env.subst(raw_script.replace('"', "").strip())
        if os.path.isfile(script):
            return script
        path = _lookup_in_ldpath(script)
        if path:
            return path

    if script:
        sys.stderr.write(
            "Error: Could not find '%s' LD script in LDPATH '%s'\n"
            % (script, env.subst("$LIBPATH"))
        )
        env.Exit(1)

    if not script and "LDSCRIPT_PATH" in env:
        path = _lookup_in_ldpath(env["LDSCRIPT_PATH"])
        if path:
            return path

    sys.stderr.write("Error: Could not find LD script\n")
    env.Exit(1)


def ConfigureDebugTarget(env):
    def _cleanup_debug_flags(scope):
        if scope not in env:
            return
        unflags = ["-Os", "-g"]
        for level in [0, 1, 2, 3]:
            for flag in ("O", "g", "ggdb"):
                unflags.append("-%s%d" % (flag, level))
        env[scope] = [f for f in env.get(scope, []) if f not in unflags]

    env.Append(CPPDEFINES=["__PLATFORMIO_BUILD_DEBUG__"])

    for scope in ("ASFLAGS", "CCFLAGS", "LINKFLAGS"):
        _cleanup_debug_flags(scope)

    debug_flags = env.ParseFlags(
        env.get("PIODEBUGFLAGS")
        if env.get("PIODEBUGFLAGS")
        and not env.GetProjectOptions(as_dict=True).get("debug_build_flags")
        else env.GetProjectOption("debug_build_flags")
    )

    env.MergeFlags(debug_flags)
    optimization_flags = [
        f for f in debug_flags.get("CCFLAGS", []) if f.startswith(("-O", "-g"))
    ]

    if optimization_flags:
        env.AppendUnique(
            ASFLAGS=[
                # skip -O flags for assembler
                f
                for f in optimization_flags
                if f.startswith("-g")
            ],
            LINKFLAGS=optimization_flags,
        )


def GetExtraScripts(env, scope):
    items = []
    for item in env.GetProjectOption("extra_scripts", []):
        if scope == "post" and ":" not in item:
            items.append(item)
        elif item.startswith("%s:" % scope):
            items.append(item[len(scope) + 1 :])
    if not items:
        return items
    with fs.cd(env.subst("$PROJECT_DIR")):
        return [os.path.abspath(env.subst(item)) for item in items]


def generate(env):
    env.AddMethod(GetCompilerType)
    env.AddMethod(GetActualLDScript)
    env.AddMethod(ConfigureDebugTarget)
    env.AddMethod(GetExtraScripts)
    # bakward-compatibility with Zephyr build script
    env.AddMethod(ConfigureDebugTarget, "ConfigureDebugFlags")


def exists(_):
    return True
