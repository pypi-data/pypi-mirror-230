#    Copyright 2020 - present Jonas Waeber
#
#    Licensed under the Apache License, Version 2.0 (the 'License');
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an 'AS IS' BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

from init_client import client, world_id

if __name__ == '__main__':
    test_category_1 = client.category.put(
        {
            'title': 'Test Creation Category',
            'world': {
                'id': world_id
            }
        }
    )
    print(test_category_1)
    test_category_2 = client.category.put(
        {
            'title': 'Test Creation Category 2',
            'world': {
                'id': world_id
            }
        }
    )
    print(test_category_2)
    response_patch_article_2 = client.category.patch(
        test_category_2['id'],
        {
            'excerpt': 'This is an excerpt for an article.'
        }
    )
    print(response_patch_article_2)
    full_test_category_2 = client.category.get(
        test_category_2['id'],
        2
    )
    print(full_test_category_2)
    assert full_test_category_2['excerpt'] == 'This is an excerpt for an article.'
    list_of_articles_no_category = client.category.articles(world_id, "-1")
    print(list_of_articles_no_category)

    client.category.delete(test_category_1['id'])
    client.category.delete(test_category_2['id'])
