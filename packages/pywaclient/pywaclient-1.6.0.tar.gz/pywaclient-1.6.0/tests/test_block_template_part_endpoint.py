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
    test_block_template_part_1 = client.block_template_part.put(
        {
            'title': 'Test block_template_part Creation',
            'templateType': 'block_template_part',
            'world': {
                'id': world_id}
        }
    )
    test_block_template_part_2 = client.block_template_part.put(
        {
            'title': 'Test block_template_part Creation 2',
            'templateType': 'block_template_part',
            'world': {
                'id': world_id}
        }
    )
    response_patch_block_template_part_2 = client.block_template_part.patch(
        test_block_template_part_2['id'],
        {
            'excerpt': 'This is an excerpt for an block_template_part.'
        }
    )

    full_test_block_template_part_2 = client.block_template_part.get(
        test_block_template_part_2['id'],
        2
    )

    assert full_test_block_template_part_2['excerpt'] == 'This is an excerpt for an block_template_part.'

    client.block_template_part.delete(test_block_template_part_1['id'])
    client.block_template_part.delete(test_block_template_part_2['id'])

    block_template_part_with_a_lot_of_views = client.block_template_part.put(
        {
            'title': 'An block_template_part with a lot of views.',
            'templateType': 'block_template_part',
            'world': {
                'id': world_id
            }
        }
    )
    print(client.block_template_part.get(block_template_part_with_a_lot_of_views['id'], 2))
