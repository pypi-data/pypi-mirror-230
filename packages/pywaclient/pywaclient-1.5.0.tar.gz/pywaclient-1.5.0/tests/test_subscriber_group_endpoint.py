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
import json

from init_client import world_id, user, client

if __name__ == '__main__':

    group = client.subscriber_group.put(
        {
            'title': 'Test Subscriber Group Creation',
            'world': {
                'id': world_id
            }
        }
    )

    client.subscriber_group.patch(group['id'],
                                  {
                                      'title': 'A new title',
                                      'description': 'A different description',
                                      'position': 100,
                                      'isHidden': False,
                                      'isAssignable': False,
                                      'tags': 'anew,tag,a,day',
                                      'isDefault': False,
                                      'paidsubscribers': [
                                          {
                                              'id': user['id']
                                          }
                                      ]
                                  }
                                  )

    group = client.subscriber_group.get(group['id'], 2)
    print(json.dumps(group, indent=2))

    client.subscriber_group.delete(group['id'])
