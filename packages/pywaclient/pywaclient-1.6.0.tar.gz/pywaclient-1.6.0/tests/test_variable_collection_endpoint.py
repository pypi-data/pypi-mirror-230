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
    test_variableCollection_2 = client.variable_collection.put(
        {
            "title": "Variables Collection 2",
            "description": "All variables used in this world.",
            "world": world_id,
            "prefix": "test-prefix-2",
            "state": "public"
        }
    )
    response_patch_variableCollection_2 = client.variable_collection.patch(
        test_variableCollection_2['id'],
        {
            'description': 'Update this variable collection with a new excerpt.'
        }
    )

    full_test_variableCollection_2 = client.variable_collection.get(
        test_variableCollection_2['id'],
        2
    )

    assert full_test_variableCollection_2['description'] == 'Update this variable collection with a new excerpt.'

    for i in range(50):
        test_variable_1 = client.variable.put(
            {
                "k": str(i),
                "t": "title",
                "v": "value",
                "type": "string",
                "collection": test_variableCollection_1['id'],
                "world": world_id
            }
        )

    for x in client.variable_collection.variables(world_id, test_variableCollection_1['id']):
        print(x)

    # client.variableCollection.delete(test_variableCollection_1['id'])
    client.variable_collection.delete(test_variableCollection_2['id'])
