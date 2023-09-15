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

import click

from superide.exception import PlatformioException
from superide.project.helpers import get_project_dir

# pylint: disable=too-many-instance-attributes, redefined-builtin
# pylint: disable=too-many-arguments


class DefectItem:
    SEVERITY_HIGH = 1
    SEVERITY_MEDIUM = 2
    SEVERITY_LOW = 4
    SEVERITY_LABELS = {4: "low", 2: "medium", 1: "high"}

    def __init__(
        self,
        severity,
        category,
        message,
        file=None,
        line=0,
        column=0,
        id=None,
        callstack=None,
        cwe=None,
    ):
        assert severity in (self.SEVERITY_HIGH, self.SEVERITY_MEDIUM, self.SEVERITY_LOW)
        self.severity = severity
        self.category = category
        self.message = message
        self.line = int(line)
        self.column = int(column)
        self.callstack = callstack
        self.cwe = cwe
        self.id = id
        self.file = file or "unknown"
        if file.lower().startswith(get_project_dir().lower()):
            self.file = os.path.relpath(file, get_project_dir())

    def __repr__(self):
        defect_color = None
        if self.severity == self.SEVERITY_HIGH:
            defect_color = "red"
        elif self.severity == self.SEVERITY_MEDIUM:
            defect_color = "yellow"

        format_str = "{file}:{line}: [{severity}:{category}] {message} {id}"
        return format_str.format(
            severity=click.style(self.SEVERITY_LABELS[self.severity], fg=defect_color),
            category=click.style(self.category.lower(), fg=defect_color),
            file=click.style(self.file, bold=True),
            message=self.message,
            line=self.line,
            id="%s" % "[%s]" % self.id if self.id else "",
        )

    def __or__(self, defect):
        return self.severity | defect.severity

    @staticmethod
    def severity_to_int(label):
        for key, value in DefectItem.SEVERITY_LABELS.items():
            if label == value:
                return key
        raise PlatformioException("Unknown severity label -> %s" % label)

    def as_dict(self):
        return {
            "severity": self.SEVERITY_LABELS[self.severity],
            "category": self.category,
            "message": self.message,
            "file": os.path.abspath(self.file),
            "line": self.line,
            "column": self.column,
            "callstack": self.callstack,
            "id": self.id,
            "cwe": self.cwe,
        }
