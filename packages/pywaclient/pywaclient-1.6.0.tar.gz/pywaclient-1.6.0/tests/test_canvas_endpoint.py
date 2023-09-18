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
    test_canvas_1 = client.canvas.put(
        {
            "title": "Organization Whiteboard",
            "data": {"title": "Test"},
            "world": {
                "id": world_id
            }
        }
    )
    test_canvas_2 = client.canvas.put(
        {
            'title': 'Test Canvas Creation 2',
            'templateType': 'canvas',
            'world': {
                'id': world_id}
        }
    )
    response_patch_canvas_2 = client.canvas.patch(
        test_canvas_2['id'],
        {
            'excerpt': 'This is an excerpt for an canvas.'
        }
    )

    full_test_canvas_2 = client.canvas.get(
        test_canvas_2['id'],
        2
    )

    assert full_test_canvas_2['excerpt'] == 'This is an excerpt for an canvas.'

    client.canvas.delete(test_canvas_1['id'])
    client.canvas.delete(test_canvas_2['id'])

    canvas_with_a_lot_of_views = client.canvas.put(
        {
            'title': 'An canvas with a lot of views.',
            'templateType': 'canvas',
            'world': {
                'id': world_id
            }
        }
    )
    print(client.canvas.get(canvas_with_a_lot_of_views['id'], 2))
