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

import datetime
import json
import os

import click

from superide.test.reports.base import TestReportBase
from superide.test.result import TestStatus


class JsonTestReport(TestReportBase):
    def generate(self, output_path, verbose=False):
        if os.path.isdir(output_path):
            output_path = os.path.join(
                output_path,
                "pio-test-report-%s-%s.json"
                % (
                    os.path.basename(self.test_result.project_dir),
                    datetime.datetime.now().strftime("%Y%m%d%H%M%S"),
                ),
            )

        with open(output_path, mode="w", encoding="utf8") as fp:
            json.dump(self.to_json(), fp)

        if verbose:
            click.secho(f"Saved JSON report to the {output_path}", fg="green")

    def to_json(self):
        result = dict(
            version="1.0",
            project_dir=self.test_result.project_dir,
            duration=self.test_result.duration,
            testcase_nums=self.test_result.case_nums,
            error_nums=self.test_result.get_status_nums(TestStatus.ERRORED),
            failure_nums=self.test_result.get_status_nums(TestStatus.FAILED),
            skipped_nums=self.test_result.get_status_nums(TestStatus.SKIPPED),
            test_suites=[],
        )
        for test_suite in self.test_result.suites:
            result["test_suites"].append(self.test_suite_to_json(test_suite))
        return result

    def test_suite_to_json(self, test_suite):
        result = dict(
            env_name=test_suite.env_name,
            test_name=test_suite.test_name,
            test_dir=test_suite.test_dir,
            status=test_suite.status.name,
            duration=test_suite.duration,
            timestamp=datetime.datetime.fromtimestamp(test_suite.timestamp).strftime(
                "%Y-%m-%dT%H:%M:%S"
            )
            if test_suite.timestamp
            else None,
            testcase_nums=len(test_suite.cases),
            error_nums=test_suite.get_status_nums(TestStatus.ERRORED),
            failure_nums=test_suite.get_status_nums(TestStatus.FAILED),
            skipped_nums=test_suite.get_status_nums(TestStatus.SKIPPED),
            test_cases=[],
        )
        for test_case in test_suite.cases:
            result["test_cases"].append(self.test_case_to_json(test_case))
        return result

    @staticmethod
    def test_case_to_json(test_case):
        result = dict(
            name=test_case.name,
            status=test_case.status.name,
            message=test_case.message,
            stdout=test_case.stdout,
            duration=test_case.duration,
            exception=None,
            source=None,
        )
        if test_case.exception:
            result["exception"] = "%s: %s" % (
                test_case.exception.__class__.__name__,
                test_case.exception,
            )
        if test_case.source:
            result["source"] = dict(
                file=test_case.source.filename, line=test_case.source.line
            )
        return result
