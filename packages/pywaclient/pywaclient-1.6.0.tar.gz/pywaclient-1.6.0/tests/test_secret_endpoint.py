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
    test_article_1 = client.article.put(
        {
            'title': 'Secret Article',
            'templateType': 'article',
            'world': {
                'id': world_id}
        }
    )
    test_article_2 = client.article.put(
        {
            'title': 'Secret Article 2',
            'templateType': 'article',
            'world': {
                'id': world_id
            }
        }
    )

    test_subscriber_group_1 = client.subscriber_group.put(
        {
            'title': 'A Secret Subscriber Group',
            'world': {
                'id': world_id
            }
        }
    )

    test_subscriber_group_2 = client.subscriber_group.put(
        {
            'title': 'A Secret Subscriber Group 2',
            'world': {
                'id': world_id
            }
        }
    )

    test_subscriber_group_3 = client.subscriber_group.put(
        {
            'title': 'A Secret Subscriber Group 3',
            'world': {
                'id': world_id
            }
        }
    )

    test_secret_1 = client.secret.put(
        {
            'title': 'Test Secret Creation',
            "content": "This is some content for the secret.",
            "article": {
                "id": test_article_1['id']
            },
            'world': {
                'id': world_id
            },
            'subscribergroups': [
                {
                    'id': test_subscriber_group_1['id']
                }
            ]
        }
    )
    test_secret_2 = client.secret.put(
        {
            'title': 'Test Secret Creation 2',
            'world': {
                'id': world_id
            }
        }
    )
    response_patch_secret_2 = client.secret.patch(
        test_secret_2['id'],
        {
            'title': 'New Title',
            'content': 'The new content for an secret.',
            'article': {
                'id': test_article_1['id']
            },
            'subscribergroups': [
                {
                    'id': test_subscriber_group_2
                }
            ],
            'tags': 'some,other,tags'
        }
    )

    full_test_secret_2 = client.secret.get(
        test_secret_2['id'],
        1
    )
    assert full_test_secret_2['title'] == 'New Title'
    assert full_test_secret_2['content'] == 'The new content for an secret.'
    assert full_test_secret_2['tags'] == 'some,other,tags'
    assert full_test_secret_2['article']['id'] == test_article_1['id']
    assert full_test_secret_2['subscribergroups'][0]['id'] == test_subscriber_group_2['id']
    assert len(full_test_secret_2['subscribergroups']) == 1

    full_test_secret_2['subscribergroups'].append(
        {
            'id': test_subscriber_group_3['id']
        }
    )
    client.secret.patch(
        test_secret_2['id'],
        {
            'subscribergroups': full_test_secret_2['subscribergroups']
        }
    )
    full_test_secret_2 = client.secret.get(
        test_secret_2['id'],
        1
    )

    print(full_test_secret_2)
    assert len(full_test_secret_2['subscribergroups']) == 2

    client.secret.delete(test_secret_1['id'])
    client.secret.delete(test_secret_2['id'])

    client.article.delete(test_article_1['id'])
    client.article.delete(test_article_2['id'])

    client.subscriber_group.delete(test_subscriber_group_1['id'])
    client.subscriber_group.delete(test_subscriber_group_2['id'])
    client.subscriber_group.delete(test_subscriber_group_3['id'])