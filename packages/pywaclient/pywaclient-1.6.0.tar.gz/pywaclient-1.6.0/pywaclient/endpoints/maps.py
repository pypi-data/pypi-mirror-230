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


class MapMarkerCrudEndpoint(CrudEndpoint):

    def __init__(self, client: 'BoromirApiClient'):
        super().__init__(client, 'marker')


class MapMarkerGroupCrudEndpoint(CrudEndpoint):

    def __init__(self, client: 'BoromirApiClient'):
        super().__init__(client, 'markergroup')
        self.marker = MapMarkerCrudEndpoint(client)
        self.path_markers = 'markergroup/markers'

    def markers(self, map_maker_group_id: str) -> Iterable[Dict[str, Any]]:
        """Iterate over all map markers in a map marker group.
        """
        return self._scroll_collection(self.path_markers, {'id': map_maker_group_id}, 'entities')


class MapLayerCrudEndpoint(CrudEndpoint):

    def __init__(self, client: 'BoromirApiClient'):
        super().__init__(client, 'layer')


class MapCrudEndpoint(CrudEndpoint):

    def __init__(self, client: 'BoromirApiClient'):
        super().__init__(client, 'map')
        self.path_layers = f'{self.path}/layers'
        self.layer = MapLayerCrudEndpoint(client)
        self.path_groups = f'{self.path}/markergroups'
        self.marker_group = MapMarkerGroupCrudEndpoint(client)
        self.path_markers = f'{self.path}/markers'
        self.marker = MapMarkerCrudEndpoint(client)

    def marker_groups(self, map_id: str) -> Iterable[Dict[str, Any]]:
        """
        List the marker groups of a specific map.

        :param map_id:      The id of the map.
        :return:            Iterable of all marker groups.
        """
        return self._scroll_collection(self.path_groups, {'id': map_id}, 'entities')

    def layers(self, map_id: str) -> Iterable[Dict[str, Any]]:
        """
        List the layers of a specific map.

        :param map_id:      The id of the map.
        :return:            Iterable of all layers.
        """
        return self._scroll_collection(self.path_layers, {'id': map_id}, 'entities')

    def markers(self, map_id: str) -> Iterable[Dict[str, Any]]:
        """
        List the markers of a specific map.

        :param map_id:      The id of the map.
        :return:            Iterable of all markers.
        """
        return self._scroll_collection(self.path_markers, {'id': map_id}, 'entities')
