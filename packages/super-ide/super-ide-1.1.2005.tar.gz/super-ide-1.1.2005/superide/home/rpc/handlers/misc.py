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
import time

from superide.cache import ContentCache
from superide.compat import aio_create_task
from superide.home.rpc.handlers.base import BaseRPCHandler
from superide.home.rpc.handlers.os import OSRPC


class MiscRPC(BaseRPCHandler):
    async def load_latest_tweets(self, data_url):
        cache_key = ContentCache.key_from_args(data_url, "tweets")
        cache_valid = "180d"
        with ContentCache() as cc:
            cache_data = cc.get(cache_key)
            if cache_data:
                cache_data = json.loads(cache_data)
                # automatically update cache in background every 12 hours
                if cache_data["time"] < (time.time() - (3600 * 12)):
                    aio_create_task(
                        self._preload_latest_tweets(data_url, cache_key, cache_valid)
                    )
                return cache_data["result"]

        return await self._preload_latest_tweets(data_url, cache_key, cache_valid)

    @staticmethod
    async def _preload_latest_tweets(data_url, cache_key, cache_valid):
        result = json.loads((await OSRPC.fetch_content(data_url)))
        with ContentCache() as cc:
            cc.set(
                cache_key,
                json.dumps({"time": int(time.time()), "result": result}),
                cache_valid,
            )
        return result
