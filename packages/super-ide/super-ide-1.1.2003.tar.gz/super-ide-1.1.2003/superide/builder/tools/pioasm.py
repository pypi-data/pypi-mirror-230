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

import SCons.Tool.asm  # pylint: disable=import-error

#
# Resolve https://github.com/superide/superide-core/issues/3917
# Avoid forcing .S to bare assembly on Windows OS
#

if ".S" in SCons.Tool.asm.ASSuffixes:
    SCons.Tool.asm.ASSuffixes.remove(".S")
if ".S" not in SCons.Tool.asm.ASPPSuffixes:
    SCons.Tool.asm.ASPPSuffixes.append(".S")


generate = SCons.Tool.asm.generate
exists = SCons.Tool.asm.exists
