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
    test_chronicles_1 = client.chronicle.put(
        {
            "title": "Chronicle of the World",
            "world": {
                "id": world_id
            }
        }
    )
    test_chronicles_2 = client.chronicle.put(
        {
            'title': 'Test Chronicles Creation 2',
            'templateType': 'chronicles',
            'world': {
                'id': world_id}
        }
    )
    response_patch_chronicles_2 = client.chronicle.patch(
        test_chronicles_2['id'],
        {
            'excerpt': 'This is an excerpt for an chronicles.'
        }
    )

    full_test_chronicles_2 = client.chronicle.get(
        test_chronicles_2['id'],
        2
    )

    assert full_test_chronicles_2['excerpt'] == 'This is an excerpt for an chronicles.'

    client.chronicle.delete(test_chronicles_1['id'])
    client.chronicle.delete(test_chronicles_2['id'])

    chronicles_with_a_lot_of_views = client.chronicle.put(
        {
            'title': 'An chronicles with a lot of views.',
            'templateType': 'chronicles',
            'world': {
                'id': world_id
            }
        }
    )
    print(client.chronicle.get(chronicles_with_a_lot_of_views['id'], 2))
