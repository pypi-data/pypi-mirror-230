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

import importlib

from superide.test.result import TestResult


class TestReportBase:
    def __init__(self, test_result):
        self.test_result = test_result

    def generate(self, output_path, verbose):
        raise NotImplementedError()


class TestReportFactory:
    @staticmethod
    def new(format, test_result) -> TestReportBase:  # pylint: disable=redefined-builtin
        assert isinstance(test_result, TestResult)
        mod = importlib.import_module(f"superide.test.reports.{format}")
        report_cls = getattr(mod, "%sTestReport" % format.lower().capitalize())
        return report_cls(test_result)
