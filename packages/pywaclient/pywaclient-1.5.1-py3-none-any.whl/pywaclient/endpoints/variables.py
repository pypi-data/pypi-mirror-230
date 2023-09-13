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


class VariableCrudEndpoint(CrudEndpoint):

    def __init__(self, client: 'BoromirApiClient'):
        super().__init__(client, 'variable')


class VariableCollectionCrudEndpoint(CrudEndpoint):

    def __init__(self, client: 'BoromirApiClient'):
        super().__init__(client, 'variablecollection')
        self.variable = VariableCrudEndpoint(client)
        self.path_variables = f"{self.path}/variables"

    def variables(self, world_id: str, variable_collection_id: str, complete: bool = True, limit: int = 50,
                  offset: int = 0) -> Iterable[Dict[str, Any]]:
        """
        List all variables by a category given, filtered with a limit of entities shown and an offset.

        :param world_id:                The id of the world the variables should be returned from.
        :param variable_collection_id:  The id of the variable collection to return the variables from.
        :param complete                 Ignore limit and offset and return all the variables as an iterable. Will fetch a new batch
                                        every 50 variables.
        :param limit:                   Determines how many variables are returned. Value between 1 and 50.
        :param offset:                  Determines the offset at which variables are returned. Has to be a positive integer.
        :return:
        """
        if complete:
            return self._scroll_collection(self.path_variables, {'id': world_id}, 'entities', 'variableCollection',
                                           variable_collection_id)
        return self._post_request(self.path_variables,
                                  {'id': world_id},
                                  {'limit': limit, 'offset': offset,
                                   'variableCollection': {'id': variable_collection_id}})['entities']
