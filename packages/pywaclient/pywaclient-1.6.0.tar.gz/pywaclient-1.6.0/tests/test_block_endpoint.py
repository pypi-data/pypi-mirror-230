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

from init_client import client

if __name__ == '__main__':
    test_block_1 = client.block.put(
        {
            "title": "New Block",
            "RPGSRD": {
                "id": "273"
            },
            'template': {
                'id': '27'
            }
        }
    )
    print(test_block_1)
    test_block_2 = client.block.put(
        {
            "title": "New Block",
            "RPGSRD": {
                "id": "273"
            }
        }
    )
    print(client.block.get(test_block_2['id'], 1))
    response_patch_block_2 = client.block.patch(
        test_block_2['id'],
        {
            'textualdata': 'This is some content for the text block.'
        }
    )

    full_test_block_2 = client.block.get(
        test_block_2['id'],
        2
    )

    assert full_test_block_2['textualdata'] == 'This is some content for the text block.'
    print(full_test_block_2)
    client.block.delete(test_block_1['id'])
    client.block.delete(test_block_2['id'])

    client.block.delete('1203149')