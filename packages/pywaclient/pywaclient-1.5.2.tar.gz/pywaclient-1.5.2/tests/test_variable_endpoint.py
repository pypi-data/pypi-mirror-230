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

from init_client import world_id, client

if __name__ == '__main__':
    test_variableCollection_1 = client.variable_collection.put(
        {
            "title": "Variables Collection",
            "description": "All variables used in this world.",
            "world": world_id,
            "prefix": "test-prefix",
            "state": "public"
        }
    )
    test_variable_1 = client.variable.put(
        {
            "k": "key",
            "v": "value",
            "type": "string",
            "collection": test_variableCollection_1['id'],
            "world": world_id
        }
    )
    response_patch_variable_1 = client.variable.patch(
        test_variable_1['id'],
        {
            'v': 'This is a new value for the variable.'
        }
    )

    full_test_variable_1 = client.variable.get(
        test_variable_1['id'],
        2
    )

    assert full_test_variable_1['v'] == 'This is a new value for the variable.'

    client.variable_collection.delete(test_variableCollection_1['id'])
    client.variable.delete(test_variable_1['id'])
