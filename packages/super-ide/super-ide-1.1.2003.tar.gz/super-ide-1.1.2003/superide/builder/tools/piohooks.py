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


def AddActionWrapper(handler):
    def wraps(env, files, action):
        if not isinstance(files, (list, tuple, set)):
            files = [files]
        known_nodes = []
        unknown_files = []
        for item in files:
            nodes = env.arg2nodes(item, env.fs.Entry)
            if nodes and nodes[0].exists():
                known_nodes.extend(nodes)
            else:
                unknown_files.append(item)
        if unknown_files:
            env.Append(**{"_PIO_DELAYED_ACTIONS": [(handler, unknown_files, action)]})
        if known_nodes:
            return handler(known_nodes, action)
        return []

    return wraps


def ProcessDelayedActions(env):
    for func, nodes, action in env.get("_PIO_DELAYED_ACTIONS", []):
        func(nodes, action)


def generate(env):
    env.Replace(**{"_PIO_DELAYED_ACTIONS": []})
    env.AddMethod(AddActionWrapper(env.AddPreAction), "AddPreAction")
    env.AddMethod(AddActionWrapper(env.AddPostAction), "AddPostAction")
    env.AddMethod(ProcessDelayedActions)


def exists(_):
    return True
