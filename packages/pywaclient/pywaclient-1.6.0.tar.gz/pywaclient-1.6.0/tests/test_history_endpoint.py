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
    for history in client.world.histories(world_id):
        print(history['title'])
        client.history.delete(history['id'])

    test_timeline_1 = client.timeline.put(
        {
            'title': 'Test Timeline Creation',
            'world': {
                'id': world_id
            }
        }
    )

    test_histories_1 = client.history.put(
        {
            'title': 'Test Histories Creation',
            "year":"5545",
            'world': {
                'id': world_id
            }
        }
    )
    test_histories_2 = client.history.put(
        {
            'title': 'Test Histories Creation 2',
            'year': '2992',
            'world': {
                'id': world_id
            },
            # 'timelines': [
            #     {
            #         'id': test_timeline_1['id']
            #     }
            #]
        }
    )
    response_patch_histories_2 = client.history.patch(
        test_histories_2['id'],
        {
            'hour': '2001ad'
        }
    )

    full_test_histories_2 = client.history.get(
        test_histories_2['id'],
        2
    )

    assert full_test_histories_2['hour'] == 2001

    client.history.delete(test_histories_1['id'])
    client.history.delete(test_histories_2['id'])
    client.history.delete(test_timeline_1['id'])

    for history in client.world.histories(world_id):
        client.history.delete(history['id'])
