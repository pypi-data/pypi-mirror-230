#    Copyright 2020 - present Jonas Waeber
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
import os

from api import BoromirApiClient
from models.user import User

world_id = 'daae0a12-f3c3-4978-b571-b5313e3c1741'
client = BoromirApiClient(
    name='TEST APPLICATION',
    url='https://gitlab.com/SoulLink/world-anvil-api-client',
    application_key=os.environ.get('WA_APPLICATION_KEY'),
    authentication_token=os.environ.get('WA_AUTH_TOKEN'),
    version='0.1.0'
)
user = User(client, client.user.identity()['id'])