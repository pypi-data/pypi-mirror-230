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

class NoteCrudEndpoint(CrudEndpoint):

    def __init__(self, client: 'BoromirApiClient'):
        super().__init__(client, 'note')



class NoteSectionCrudEndpoint(CrudEndpoint):

    def __init__(self, client: 'BoromirApiClient'):
        super().__init__(client, 'notesection')
        self.note = NoteCrudEndpoint(client)
        self.note_sections_path = f'{self.path}/notes'

    def notes(self, note_section_id: str, complete: bool = True, limit: int = 50, offset: int = 0) -> Iterable[Dict[str, Any]]:
        """
        Retrieve an iterable of all the note references within one section.

        :param note_section_id: The id of the parent note section.
        :param complete:        Ignore the limit and offsets and return all the entities.
        :param limit:           The number of returned references between 1 and 50.
        :param offset:          The offset in the returned list.
        :return:
        """
        if complete:
            return self._scroll_collection(self.note_sections_path, {'id': note_section_id}, 'entities')
        assert offset >= 0
        assert 1 <= limit <= 50
        return self._post_request(self.note_sections_path, {'id': note_section_id}, {'limit': limit, 'offset': offset})['entities']


class NotebookCrudEndpoint(CrudEndpoint):

    def __init__(self, client: 'BoromirApiClient'):
        super().__init__(client, 'notebook')
        self.note_section = NoteSectionCrudEndpoint(client)
        self.path_notebook_sections = f'{self.path}/notesections'

    def note_sections(self, notebook_id: str, complete: bool = True, limit: int = 50, offset: int = 0) -> Iterable[Dict[str, Any]]:
        """
        Retrieve an iterable of all the note section references from one notebook.

        :param notebook_id: Identifier of the parent notebook.
        :param complete:    Ignore the limit and offsets and return all the entities.
        :param limit:       The number of returned references between 1 and 50.
        :param offset:      The offset in the returned list.
        :return:
        """
        if complete:
            return self._scroll_collection(self.path_notebook_sections, {'id': notebook_id}, 'entities')
        assert offset >= 0
        assert 1 <= limit <= 50
        return self._post_request(self.path_notebook_sections, {'id': notebook_id}, {'limit': limit, 'offset': offset})['entities']