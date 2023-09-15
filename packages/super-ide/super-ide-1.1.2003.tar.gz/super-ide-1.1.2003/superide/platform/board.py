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

from superide import fs, util
from superide.compat import MISSING
from superide.debug.exception import DebugInvalidOptionsError, DebugSupportError
from superide.exception import InvalidJSONFile, UserSideException
from superide.platform.exception import InvalidBoardManifest


class PlatformBoardConfig:
    def __init__(self, manifest_path):
        self._id = os.path.basename(manifest_path)[:-5]
        assert os.path.isfile(manifest_path)
        self.manifest_path = manifest_path
        try:
            self._manifest = fs.load_json(manifest_path)
        except InvalidJSONFile as exc:
            raise InvalidBoardManifest(manifest_path) from exc
        if not set(["name", "url", "vendor"]) <= set(self._manifest):
            raise UserSideException(
                "Please specify name, url and vendor fields for " + manifest_path
            )

    def get(self, path, default=MISSING):
        try:
            value = self._manifest
            for k in path.split("."):
                value = value[k]
            return value
        except KeyError:
            if default != MISSING:
                return default
        raise KeyError("Invalid board option '%s'" % path)

    def update(self, path, value):
        newdict = None
        for key in path.split(".")[::-1]:
            if newdict is None:
                newdict = {key: value}
            else:
                newdict = {key: newdict}
        util.merge_dicts(self._manifest, newdict)

    def __contains__(self, key):
        try:
            self.get(key)
            return True
        except KeyError:
            return False

    @property
    def id(self):
        return self._id

    @property
    def id_(self):
        return self.id

    @property
    def manifest(self):
        return self._manifest

    def get_brief_data(self):
        result = {
            "id": self.id,
            "name": self._manifest["name"],
            "platform": self._manifest.get("platform"),
            "mcu": self._manifest.get("build", {}).get("mcu", "").upper(),
            "fcpu": int(
                "".join(
                    [
                        c
                        for c in str(self._manifest.get("build", {}).get("f_cpu", "0L"))
                        if c.isdigit()
                    ]
                )
            ),
            "ram": self._manifest.get("upload", {}).get("maximum_ram_size", 0),
            "rom": self._manifest.get("upload", {}).get("maximum_size", 0),
            "frameworks": self._manifest.get("frameworks"),
            "vendor": self._manifest["vendor"],
            "url": self._manifest["url"],
        }
        if self._manifest.get("connectivity"):
            result["connectivity"] = self._manifest.get("connectivity")
        debug = self.get_debug_data()
        if debug:
            result["debug"] = debug
        return result

    def get_debug_data(self):
        if not self._manifest.get("debug", {}).get("tools"):
            return None
        tools = {}
        for name, options in self._manifest["debug"]["tools"].items():
            tools[name] = {}
            for key, value in options.items():
                if key in ("default", "onboard") and value:
                    tools[name][key] = value
        return {"tools": tools}

    def get_debug_tool_name(self, custom=None):
        debug_tools = self._manifest.get("debug", {}).get("tools")
        tool_name = custom
        if tool_name == "custom":
            return tool_name
        if not debug_tools:
            raise DebugSupportError(self._manifest["name"])
        if tool_name:
            if tool_name in debug_tools:
                return tool_name
            raise DebugInvalidOptionsError(
                "Unknown debug tool `%s`. Please use one of `%s` or `custom`"
                % (tool_name, ", ".join(sorted(list(debug_tools))))
            )

        # automatically select best tool
        data = {"default": [], "onboard": [], "external": []}
        for key, value in debug_tools.items():
            if value.get("default"):
                data["default"].append(key)
            elif value.get("onboard"):
                data["onboard"].append(key)
            data["external"].append(key)

        for key, value in data.items():
            if not value:
                continue
            return sorted(value)[0]

        assert any(item for item in data)
