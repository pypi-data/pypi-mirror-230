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
from typing import Iterable

from pywaclient.endpoints import CrudEndpoint, download_binary


class ImageCrudEndpoint(CrudEndpoint):

    def __init__(self, client: 'BoromirApiClient'):
        super().__init__(client, 'image')

    def get_binary(self, identifier: str) -> Iterable[bytes]:
        """Get the image binary by identifier

        :param identifier: Identifier of the image.
        :return: Iterable of image binary chunks.
        """
        metadata = self.get(identifier, -1)
        return download_binary(metadata['url'])
