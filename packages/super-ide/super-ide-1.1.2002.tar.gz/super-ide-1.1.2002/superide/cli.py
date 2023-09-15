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
from pathlib import Path

import click


class PlatformioCLI(click.MultiCommand):
    leftover_args = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._pio_root_path = Path(__file__).parent
        self._pio_cmd_aliases = dict(package="pkg")

    def _find_pio_commands(self):
        def _to_module_path(p):
            return (
                "superide." + ".".join(p.relative_to(self._pio_root_path).parts)[:-3]
            )

        result = {}
        for p in self._pio_root_path.rglob("cli.py"):
            # skip this module
            if p.parent == self._pio_root_path:
                continue
            cmd_name = p.parent.name
            result[self._pio_cmd_aliases.get(cmd_name, cmd_name)] = _to_module_path(p)

        # find legacy commands
        for p in (self._pio_root_path / "commands").iterdir():
            if p.name.startswith("_"):
                continue
            if (p / "command.py").is_file():
                result[p.name] = _to_module_path(p / "command.py")
            elif p.name.endswith(".py"):
                result[p.name[:-3]] = _to_module_path(p)

        return result

    @staticmethod
    def in_silence():
        args = PlatformioCLI.leftover_args
        return args and any(
            [
                args[0] == "debug" and "--interpreter" in " ".join(args),
                args[0] == "upgrade",
                "--json-output" in args,
                "--version" in args,
            ]
        )

    @classmethod
    def reveal_cmd_path_args(cls, ctx):
        result = []
        group = ctx.command
        args = cls.leftover_args[::]
        while args:
            cmd_name = args.pop(0)
            next_group = group.get_command(ctx, cmd_name)
            if next_group:
                group = next_group
                result.append(cmd_name)
            if not hasattr(group, "get_command"):
                break
        return result

    def invoke(self, ctx):
        PlatformioCLI.leftover_args = ctx.args
        if hasattr(ctx, "protected_args"):
            PlatformioCLI.leftover_args = ctx.protected_args + ctx.args
        return super().invoke(ctx)

    def list_commands(self, ctx):
        return sorted(list(self._find_pio_commands()))

    def get_command(self, ctx, cmd_name):
        commands = self._find_pio_commands()
        if cmd_name not in commands:
            return self._handle_obsolate_command(ctx, cmd_name)
        module = importlib.import_module(commands[cmd_name])
        return getattr(module, "cli")

    @staticmethod
    def _handle_obsolate_command(ctx, cmd_name):
        # pylint: disable=import-outside-toplevel
        if cmd_name == "init":
            from superide.project.commands.init import project_init_cmd

            return project_init_cmd

        if cmd_name == "package":
            from superide.package.cli import cli

            return cli

        raise click.UsageError('No such command "%s"' % cmd_name, ctx)
