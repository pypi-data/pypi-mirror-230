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


class ManuscriptBeatCrudEndpoint(CrudEndpoint):

    def __init__(self, client: 'AragornApiClient'):
        super().__init__(client, 'manuscript_beat')


class ManuscriptPartCrudEndpoint(CrudEndpoint):

    def __init__(self, client: 'AragornApiClient'):
        super().__init__(client, 'manuscript_part')
        self._path = 'manuscript_part'
        self.beat = ManuscriptBeatCrudEndpoint(client)
        self.path_beats = f'{self.path}/manuscript_beats'

    def beats(self, identifier: str) -> Iterable[Dict[str, Any]]:
        """Retrieve an iterable of all the beats of a manuscript part.

        :param identifier:  Identifier of the manuscript version.
        :return:            Iterable dictionary of the entities.
        """
        return self._scroll_collection(self.path_beats, {'id': identifier}, 'entities')


class ManuscriptPlotCrudEndpoint(CrudEndpoint):

    def __init__(self, client: 'AragornApiClient'):
        super().__init__(client, 'manuscript_plot')


class ManuscriptStatCrudEndpoint(CrudEndpoint):

    def __init__(self, client: 'AragornApiClient'):
        super().__init__(client, 'manuscript_stat')


class ManuscriptVersionCrudEndpoint(CrudEndpoint):

    def __init__(self, client: 'AragornApiClient'):
        super().__init__(client, 'manuscript_version')
        self.part = ManuscriptPartCrudEndpoint(client)
        self.path_parts = f'{self.path}/manuscript_parts'
        self.plot = ManuscriptPlotCrudEndpoint(client)
        self.path_plots = f'{self.path}/manuscript_plots'
        self.stat = ManuscriptStatCrudEndpoint(client)
        self.path_stats = f'{self.path}/manuscript_stats'

    def parts(self, identifier: str) -> Iterable[Dict[str, Any]]:
        """Retrieve an iterable of all the parts of a manuscript version.

        :param identifier:  Identifier of the manuscript version.
        :return:            Iterable dictionary of the entities.
        """
        return self._scroll_collection(self.path_parts, {'id': identifier}, 'entities')

    def plots(self, identifier: str) -> Iterable[Dict[str, Any]]:
        """Retrieve an iterable of all the plots of a manuscript version.

        :param identifier:  Identifier of the manuscript version.
        :return:            Iterable dictionary of the entities.
        """
        return self._scroll_collection(self.path_plots, {'id': identifier}, 'entities')

    def stats(self, identifier: str) -> Iterable[Dict[str, Any]]:
        """Retrieve an iterable of all the stats of a manuscript version.

        :param identifier:  Identifier of the manuscript version.
        :return:            Iterable dictionary of the entities.
        """
        return self._scroll_collection(self.path_stats, {'id': identifier}, 'entities')


class ManuscriptBookmarkCrudEndpoint(CrudEndpoint):

    def __init__(self, client: 'BoromirApiClient'):
        super().__init__(client, 'manuscript_bookmark')


class ManuscriptTagCrudEndpoint(CrudEndpoint):

    def __init__(self, client: 'BoromirApiClient'):
        super().__init__(client, 'manuscript_tag')


class ManuscriptLabelCrudEndpoint(CrudEndpoint):

    def __init__(self, client: 'BoromirApiClient'):
        super().__init__(client, 'manuscript_label')


class ManuscriptCrudEndpoint(CrudEndpoint):

    def __init__(self, client: 'BoromirApiClient'):
        super().__init__(client, 'manuscript')
        self.bookmark = ManuscriptBookmarkCrudEndpoint(client)
        self._path_bookmarks = f'{self.path}/manuscript_bookmarks'
        self.tag = ManuscriptTagCrudEndpoint(client)
        self._path_tags = f'{self.path}/manuscript_tags'
        self.label = ManuscriptLabelCrudEndpoint(client)
        self._path_labels = f'{self.path}/manuscript_labels'
        self.version = ManuscriptVersionCrudEndpoint(client)
        self._path_versions = f'{self.path}/manuscript_versions'

    def bookmarks(self, identifier: str) -> Iterable[Dict[str, Any]]:
        """Retrieve an iterable of all the bookmarks on a manuscript.

        :param identifier:  Identifier of the manuscript.
        :return:            Iterable dictionary of the entities.
        """
        return self._scroll_collection(self._path_bookmarks, {'id': identifier}, 'entities')

    def labels(self, identifier: str) -> Iterable[Dict[str, Any]]:
        """Retrieve an iterable of all the labels defined in a manuscript.

        :param identifier:  Identifier of the manuscript.
        :return:            Iterable dictionary of the entities.
        """
        return self._scroll_collection(self._path_labels, {'id': identifier}, 'entities')

    def tags(self, identifier: str) -> Iterable[Dict[str, Any]]:
        """Retrieve an iterable of all the tags added to a manuscript.

        :param identifier:  Identifier of the manuscript.
        :return:            Iterable dictionary of the entities.
        """
        return self._scroll_collection(self._path_tags, {'id': identifier}, 'entities')

    def versions(self, identifier: str) -> Iterable[Dict[str, Any]]:
        """Retrieve an iterable of all the versions of a manuscript.

        :param identifier:  Identifier of the manuscript.
        :return:            Iterable dictionary of the entities.
        """
        return self._scroll_collection(self._path_versions, {'id': identifier}, 'entities')
