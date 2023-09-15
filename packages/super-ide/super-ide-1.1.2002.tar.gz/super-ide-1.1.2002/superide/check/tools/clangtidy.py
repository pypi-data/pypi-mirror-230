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

import re
from os.path import join

from superide.check.defect import DefectItem
from superide.check.tools.base import CheckToolBase


class ClangtidyCheckTool(CheckToolBase):
    def tool_output_filter(self, line):  # pylint: disable=arguments-differ
        if not self.options.get("verbose") and "[clang-diagnostic-error]" in line:
            return ""

        if "[CommonOptionsParser]" in line:
            self._bad_input = True
            return line

        if any(d in line for d in ("note: ", "error: ", "warning: ")):
            return line

        return ""

    def parse_defect(self, raw_line):  # pylint: disable=arguments-differ
        match = re.match(r"^(.*):(\d+):(\d+):\s+([^:]+):\s(.+)\[([^]]+)\]$", raw_line)
        if not match:
            return raw_line

        file_, line, column, category, message, defect_id = match.groups()

        severity = DefectItem.SEVERITY_LOW
        if category == "error":
            severity = DefectItem.SEVERITY_HIGH
        elif category == "warning":
            severity = DefectItem.SEVERITY_MEDIUM

        return DefectItem(severity, category, message, file_, line, column, defect_id)

    @staticmethod
    def is_check_successful(cmd_result):
        # Note: Clang-Tidy returns 1 for not critical compilation errors,
        # so 0 and 1 are only acceptable values
        return cmd_result["returncode"] < 2

    def configure_command(self):
        tool_path = join(self.get_tool_dir("tool-clangtidy"), "clang-tidy")

        cmd = [tool_path, "--quiet"]
        flags = self.get_flags("clangtidy")
        if not (
            self.is_flag_set("--checks", flags) or self.is_flag_set("--config", flags)
        ):
            cmd.append("--checks=*")

        project_files = self.get_project_target_files(
            self.project_dir, self.options["src_filters"]
        )

        src_files = []
        for items in project_files.values():
            src_files.extend(items)

        cmd.extend(flags + src_files + ["--"])
        cmd.extend(
            ["-D%s" % d for d in self.cpp_defines + self.toolchain_defines["c++"]]
        )

        includes = []
        for inc in self.cpp_includes:
            if self.options.get("skip_packages") and inc.lower().startswith(
                self.config.get("superide", "packages_dir").lower()
            ):
                continue
            includes.append(inc)

        cmd.extend(["-I%s" % inc for inc in includes])

        return cmd
