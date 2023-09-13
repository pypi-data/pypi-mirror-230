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
    auth_user = client.user.identity()
    full_user = client.user.get(auth_user['id'], 2)

    for w in client.user.worlds(full_user['id']):
        world = client.world.get(w['id'], 1)
        print(world)

    for t in client.user.block_templates(full_user['id']):
        print(t)

    for n in client.user.notebooks(auth_user['id']):
        print(n)




