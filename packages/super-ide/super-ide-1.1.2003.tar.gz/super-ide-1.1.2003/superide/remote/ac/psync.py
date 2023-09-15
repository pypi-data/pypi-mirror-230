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

import json
import os
import zlib
from io import BytesIO

from superide.remote.ac.base import AsyncCommandBase
from superide.remote.projectsync import PROJECT_SYNC_STAGE, ProjectSync


class ProjectSyncAsyncCmd(AsyncCommandBase):
    def __init__(self, *args, **kwargs):
        self.psync = None
        self._upstream = None
        super().__init__(*args, **kwargs)

    def start(self):
        project_dir = os.path.join(
            self.options["agent_working_dir"], "projects", self.options["id"]
        )
        self.psync = ProjectSync(project_dir)
        for name in self.options["items"]:
            self.psync.add_item(os.path.join(project_dir, name), name)

    def stop(self):
        self.psync = None
        self._upstream = None
        self._return_code = PROJECT_SYNC_STAGE.COMPLETED.value

    def ac_write(self, data):
        stage = PROJECT_SYNC_STAGE.lookupByValue(data.get("stage"))

        if stage is PROJECT_SYNC_STAGE.DBINDEX:
            self.psync.rebuild_dbindex()
            return zlib.compress(json.dumps(self.psync.get_dbindex()).encode())

        if stage is PROJECT_SYNC_STAGE.DELETE:
            return self.psync.delete_dbindex(
                json.loads(zlib.decompress(data["dbindex"]))
            )

        if stage is PROJECT_SYNC_STAGE.UPLOAD:
            if not self._upstream:
                self._upstream = BytesIO()
            self._upstream.write(data["chunk"])
            if self._upstream.tell() == data["total"]:
                self.psync.decompress_items(self._upstream)
                self._upstream = None
                return PROJECT_SYNC_STAGE.EXTRACTED.value

            return PROJECT_SYNC_STAGE.UPLOAD.value

        return None
