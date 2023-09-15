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

# pylint: disable=too-many-arguments

from superide import __registry_mirror_hosts__, fs
from superide.account.client import AccountClient, AccountError
from superide.http import HTTPClient, HTTPClientError


class RegistryClient(HTTPClient):
    def __init__(self):
        endpoints = [f"https://api.{host}" for host in __registry_mirror_hosts__]
        super().__init__(endpoints)

    @staticmethod
    def allowed_private_packages():
        private_permissions = set(
            [
                "service.registry.publish-private-tool",
                "service.registry.publish-private-platform",
                "service.registry.publish-private-library",
            ]
        )
        try:
            info = AccountClient().get_account_info() or {}
            for item in info.get("packages", []):
                if set(item.keys()) & private_permissions:
                    return True
        except AccountError:
            pass
        return False

    def publish_package(  # pylint: disable=redefined-builtin
        self, owner, type, archive_path, released_at=None, private=False, notify=True
    ):
        with open(archive_path, "rb") as fp:
            return self.fetch_json_data(
                "post",
                "/v3/packages/%s/%s" % (owner, type),
                params={
                    "private": 1 if private else 0,
                    "notify": 1 if notify else 0,
                    "released_at": released_at,
                },
                headers={
                    "Content-Type": "application/octet-stream",
                    "X-PIO-Content-SHA256": fs.calculate_file_hashsum(
                        "sha256", archive_path
                    ),
                },
                data=fp,
                x_with_authorization=True,
            )

    def unpublish_package(  # pylint: disable=redefined-builtin
        self, owner, type, name, version=None, undo=False
    ):
        path = "/v3/packages/%s/%s/%s" % (owner, type, name)
        if version:
            path += "/" + version
        return self.fetch_json_data(
            "delete", path, params={"undo": 1 if undo else 0}, x_with_authorization=True
        )

    def update_resource(self, urn, private):
        return self.fetch_json_data(
            "put",
            "/v3/resources/%s" % urn,
            data={"private": int(private)},
            x_with_authorization=True,
        )

    def grant_access_for_resource(self, urn, client, level):
        return self.fetch_json_data(
            "put",
            "/v3/resources/%s/access" % urn,
            data={"client": client, "level": level},
            x_with_authorization=True,
        )

    def revoke_access_from_resource(self, urn, client):
        return self.fetch_json_data(
            "delete",
            "/v3/resources/%s/access" % urn,
            data={"client": client},
            x_with_authorization=True,
        )

    def list_resources(self, owner):
        return self.fetch_json_data(
            "get",
            "/v3/resources",
            params={"owner": owner} if owner else None,
            x_cache_valid="1h",
            x_with_authorization=True,
        )

    def list_packages(self, query=None, qualifiers=None, page=None, sort=None):
        search_query = []
        if qualifiers:
            valid_qualifiers = (
                "authors",
                "keywords",
                "frameworks",
                "platforms",
                "headers",
                "ids",
                "names",
                "owners",
                "types",
            )
            assert set(qualifiers.keys()) <= set(valid_qualifiers)
            for name, values in qualifiers.items():
                for value in set(
                    values if isinstance(values, (list, tuple)) else [values]
                ):
                    search_query.append('%s:"%s"' % (name[:-1], value))
        if query:
            search_query.append(query)
        params = dict(query=" ".join(search_query))
        if page:
            params["page"] = int(page)
        if sort:
            params["sort"] = sort
        return self.fetch_json_data(
            "get",
            "/v3/search",
            params=params,
            x_cache_valid="1h",
            x_with_authorization=self.allowed_private_packages(),
        )

    def get_package(self, typex, owner, name, version=None, extra_path=None):
        try:
            return self.fetch_json_data(
                "get",
                "/v3/packages/{owner}/{type}/{name}{extra_path}".format(
                    type=typex,
                    owner=owner.lower(),
                    name=name.lower(),
                    extra_path=extra_path or "",
                ),
                params=dict(version=version) if version else None,
                x_cache_valid="1h",
                x_with_authorization=self.allowed_private_packages(),
            )
        except HTTPClientError as exc:
            if exc.response is not None and exc.response.status_code == 404:
                return None
            raise exc
