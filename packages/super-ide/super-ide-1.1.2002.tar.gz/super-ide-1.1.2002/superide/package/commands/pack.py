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

from superide.package.manifest.parser import ManifestParserFactory
from superide.package.manifest.schema import ManifestSchema, ManifestValidationError
from superide.package.pack import PackagePacker


@click.command("pack", short_help="Create a tarball from a package")
@click.argument(
    "package",
    default=os.getcwd,
    metavar="<source directory, tar.gz or zip>",
    type=click.Path(exists=True, file_okay=True, dir_okay=True),
)
@click.option(
    "-o", "--output", help="A destination path (folder or a full path to file)"
)
def package_pack_cmd(package, output):
    p = PackagePacker(package)
    archive_path = p.pack(output)
    # validate manifest
    try:
        ManifestSchema().load_manifest(
            ManifestParserFactory.new_from_archive(archive_path).as_dict()
        )
    except ManifestValidationError as exc:
        os.remove(archive_path)
        raise exc
    click.secho('Wrote a tarball to "%s"' % archive_path, fg="green")
