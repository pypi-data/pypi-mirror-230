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

import click

from superide.test.result import TestCase, TestCaseSource, TestStatus
from superide.test.runners.base import TestRunnerBase


class GoogletestTestCaseParser:
    # Examples:
    # [ RUN      ] FooTest.Bar
    # ...
    # [  FAILED  ] FooTest.Bar (0 ms)
    STATUS__NAME_RE = r"^\[\s+(?P<status>[A-Z]+)\s+\]\s+(?P<name>[^\(\s]+)"

    # Examples:
    # [ RUN      ] FooTest.Bar
    # test/test_gtest/test_main.cpp:26: Failure
    # Y:\core\examples\unit-testing\googletest\test\test_gtest\test_main.cpp:26: Failure
    SOURCE_MESSAGE_RE = r"^(?P<source_file>.+):(?P<source_line>\d+):(?P<message>.*)$"

    def __init__(self):
        self._tmp_tc = None

    def parse(self, line):
        if self._tmp_tc:
            self._tmp_tc.stdout += line
        return self._parse_test_case(line)

    def _parse_test_case(self, line):
        status, name = self._parse_status_and_name(line)
        if status == "RUN":
            self._tmp_tc = TestCase(name, TestStatus.PASSED, stdout=line)
            return None
        if not status or not self._tmp_tc:
            return None
        source, message = self._parse_source_and_message(self._tmp_tc.stdout)
        test_case = TestCase(
            name=self._tmp_tc.name,
            status=TestStatus.from_string(status),
            message=message,
            source=source,
            stdout=self._tmp_tc.stdout.strip(),
        )
        self._tmp_tc = None
        return test_case

    def _parse_status_and_name(self, line):
        result = (None, None)
        line = line.strip()
        if not line.startswith("["):
            return result
        match = re.search(self.STATUS__NAME_RE, line)
        if not match:
            return result
        return match.group("status"), match.group("name")

    def _parse_source_and_message(self, stdout):
        for line in stdout.split("\n"):
            line = line.strip()
            if not line:
                continue
            match = re.search(self.SOURCE_MESSAGE_RE, line)
            if not match:
                continue
            return (
                TestCaseSource(
                    match.group("source_file"), int(match.group("source_line"))
                ),
                (match.group("message") or "").strip() or None,
            )
        return (None, None)


class GoogletestTestRunner(TestRunnerBase):
    EXTRA_LIB_DEPS = ["google/googletest@^1.12.1"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._tc_parser = GoogletestTestCaseParser()
        os.environ["GTEST_COLOR"] = "no"  # disable ANSI symbols

    def on_testing_line_output(self, line):
        if self.options.verbose:
            click.echo(line, nl=False)

        test_case = self._tc_parser.parse(line)
        if test_case:
            self.test_suite.add_case(test_case)
            if not self.options.verbose:
                click.echo(test_case.humanize())

        if "Global test environment tear-down" in line:
            self.test_suite.on_finish()
