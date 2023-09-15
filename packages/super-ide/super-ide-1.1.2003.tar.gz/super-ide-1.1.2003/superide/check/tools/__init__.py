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

from superide import exception
from superide.check.tools.clangtidy import ClangtidyCheckTool
from superide.check.tools.cppcheck import CppcheckCheckTool
from superide.check.tools.pvsstudio import PvsStudioCheckTool


class CheckToolFactory:
    @staticmethod
    def new(tool, project_dir, config, envname, options):
        cls = None
        if tool == "cppcheck":
            cls = CppcheckCheckTool
        elif tool == "clangtidy":
            cls = ClangtidyCheckTool
        elif tool == "pvs-studio":
            cls = PvsStudioCheckTool
        else:
            raise exception.PlatformioException("Unknown check tool `%s`" % tool)
        return cls(project_dir, config, envname, options)
