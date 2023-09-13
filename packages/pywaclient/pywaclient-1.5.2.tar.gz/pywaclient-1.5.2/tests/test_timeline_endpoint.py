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
    test_history_1 = client.history.put(
        {
            'title': 'Test History Creation',
            'year': 1000,
            'world': {
                'id': world_id
            }
        }
    )

    # test_category_1 = client.category.put(
    #     {
    #         'title': 'Test Category Creation',
    #         'world': {
    #             'id': world_id
    #         }
    #     }
    # )

    test_subscriber_group_1 = client.subscriber_group.put(
        {
            'title': 'A Secret Subscriber Group',
            'world': {
                'id': world_id
            }
        })



    test_timelines_1 = client.timeline.put(
        {
            'title': 'Test Timelines Creation',
            'state': 'private',
            'world': {
                'id': world_id
            },
            'icon': 'fa-solid fa-calendar',
            'subscribergroups': [
                {
                    'id': test_subscriber_group_1['id']
                }
            ],
            'article': {
                'id': test_article_1['id']
            },
            # 'category': {
            #     'id': test_category_1['id']
            # },
            'tags': 'test,test2',
            'histories': [
                {
                    'id': test_history_1['id']
                }
            ],
            'description': 'Test Description',
            'utdOffset': 0,
            'type': 'parallel',
            'showInToC': True,
            'calendar': {
                'id': '102144'
            }
        }
    )

    test_era = client.timeline.era.put(
        {
            'title': 'Test Era Creation #1',
            'world': {
                'id': world_id
            },
            'timeline': {
                'id': test_timelines_1['id']
            }
        }
    )
    print(test_era)
    test_timelines_2 = client.timeline.put(
        {
            'title': 'Test Timelines Creation 2',
            'world': {
                'id': world_id
            }
        }
    )
    response_patch_timelines_2 = client.timeline.patch(
        test_timelines_2['id'],
        {
            'title': 'Change the title'
        }
    )

    full_test_timelines_2 = client.timeline.get(
        test_timelines_2['id'],
        2
    )

    assert full_test_timelines_2['title'] == 'Change the title'

    client.timeline.delete(test_timelines_1['id'])
    client.timeline.delete(test_timelines_2['id'])

    client.article.delete(test_article_1['id'])
    client.history.delete(test_history_1['id'])
    # client.category.delete(test_category_1['id'])
    client.subscriber_group.delete(test_subscriber_group_1['id'])

