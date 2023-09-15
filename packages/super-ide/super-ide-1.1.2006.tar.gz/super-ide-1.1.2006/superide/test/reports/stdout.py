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

import click
from tabulate import tabulate

from superide import util
from superide.test.reports.base import TestReportBase
from superide.test.result import TestStatus


class StdoutTestReport(TestReportBase):
    def generate(self, verbose=False):  # pylint: disable=arguments-differ
        click.echo()

        tabular_data = []
        failed_nums = self.test_result.get_status_nums(TestStatus.FAILED)
        skipped_nums = self.test_result.get_status_nums(TestStatus.SKIPPED)
        is_error = failed_nums > 0 or self.test_result.is_errored

        for test_suite in self.test_result.suites:
            if not verbose and test_suite.status == TestStatus.SKIPPED:
                continue
            status_str = test_suite.status.name
            if test_suite.status in (TestStatus.FAILED, TestStatus.ERRORED):
                status_str = click.style(status_str, fg="red")
            elif test_suite.status == TestStatus.PASSED:
                status_str = click.style(status_str, fg="green")

            tabular_data.append(
                (
                    click.style(test_suite.env_name, fg="cyan"),
                    test_suite.test_name,
                    status_str,
                    util.humanize_duration_time(test_suite.duration or None),
                )
            )

        if tabular_data:
            util.print_labeled_bar(
                "SUMMARY",
                is_error=is_error,
                fg="red" if is_error else "green",
            )
            click.echo(
                tabulate(
                    tabular_data,
                    headers=[
                        click.style(s, bold=True)
                        for s in ("Environment", "Test", "Status", "Duration")
                    ],
                ),
                err=is_error,
            )

        if failed_nums:
            self.print_failed_test_cases()

        util.print_labeled_bar(
            "%d test cases: %s%s%d succeeded in %s"
            % (
                self.test_result.case_nums,
                ("%d failed, " % failed_nums) if failed_nums else "",
                ("%d skipped, " % skipped_nums) if skipped_nums else "",
                self.test_result.get_status_nums(TestStatus.PASSED),
                util.humanize_duration_time(self.test_result.duration),
            ),
            is_error=is_error,
            fg="red" if is_error else "green",
        )

    def print_failed_test_cases(self):
        click.echo()
        for test_suite in self.test_result.suites:
            if test_suite.status != TestStatus.FAILED:
                continue
            util.print_labeled_bar(
                click.style(
                    f"{test_suite.env_name}:{test_suite.test_name}", bold=True, fg="red"
                ),
                is_error=True,
                sep="_",
            )
            for test_case in test_suite.cases:
                if test_case.status != TestStatus.FAILED:
                    continue
                click.echo((test_case.stdout or "").strip())
                click.echo()
