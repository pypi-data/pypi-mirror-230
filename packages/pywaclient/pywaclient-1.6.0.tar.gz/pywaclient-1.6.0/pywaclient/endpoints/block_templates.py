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
from typing import Dict, Any, Iterable

from pywaclient.endpoints import CrudEndpoint


class BlockTemplatePartCrudEndpoint(CrudEndpoint):

    def __init__(self, client: 'BoromirApiClient'):
        super().__init__(client, 'blocktemplatepart')

class BlockTemplateCrudEndpoint(CrudEndpoint):

    def __init__(self, client: 'BoromirApiClient'):
        super().__init__(client, 'blocktemplate')
        self.path_block_template_parts = f'{self.path}/blocktemplateparts'
        self.block_template_part = BlockTemplatePartCrudEndpoint(client)

    def block_template_parts(self, block_template_id: str, complete: bool = True, limit: int = 50,
                             offset: int = 0) -> Iterable[Dict[str, Any]]:
        """
        List all parts of a block template as a list of entities.

        :param block_template_id:   The identifier of the block template.
        :param complete             Ignore limit and offset and return all the block template parts as an iterable.
        :param limit:               Determines how many articles are returned. Value between 1 and 50.
        :param offset:              Determines the offset at which articles are returned. Has to be a positive integer.
        :return:                    An iterable of block templates.
        """
        if complete:
            return self._scroll_collection(self.path_block_template_parts, {'id': block_template_id}, 'entities')
        return self._post_request(self.path_block_template_parts,
                                  {'id': block_template_id},
                                  {'limit': limit, 'offset': offset})['entities']
