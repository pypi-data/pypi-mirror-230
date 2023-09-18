#    Copyright 2020 Jonas Waeber
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
from typing import Iterable, Dict, Any

from pywaclient.endpoints.eras import EraCrudEndpoint
from pywaclient.endpoints import CrudEndpoint


class TimelineCrudEndpoint(CrudEndpoint):

    def __init__(self, client: 'BoromirApiClient'):
        super().__init__(client, 'timeline')
        self.path_eras = 'eras'
        self.era = EraCrudEndpoint(client)

    def eras(self, world_id: str, timeline_id: str, complete: bool = True, limit: int = 50,
                  offset: int = 0) -> Iterable[Dict[str, Any]]:
        """
        List all eras by a timeline given, filtered with a limit of entities shown and an offset.

        :param world_id:                The id of the world the eras should be returned from.
        :param timeline_id:             The id of the timeline to return the eras from.
        :param complete                 Ignore limit and offset and return all the eras as an iterable. Will fetch a new batch
                                        every 50 variables.
        :param limit:                   Determines how many eras are returned. Value between 1 and 50.
        :param offset:                  Determines the offset at which eras are returned. Has to be a positive integer.
        :return:
        """
        if complete:
            return self._scroll_collection(self.path_eras, {'id': world_id}, 'entities', 'timeline',
                                           timeline_id)
        return self._post_request(self.path_eras,
                                  {'id': world_id},
                                  {'limit': limit, 'offset': offset,
                                   'timeline': {'id': timeline_id}})['entities']
