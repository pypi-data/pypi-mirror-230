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
from pywaclient.endpoints.articles import ArticleCrudEndpoint
from pywaclient.endpoints.block_templates import BlockTemplateCrudEndpoint
from pywaclient.endpoints.blocks import BlockCrudEndpoint, BlockFolderCrudEndpoint
from pywaclient.endpoints.canvas import CanvasCrudEndpoint
from pywaclient.endpoints.categories import CategoryCrudEndpoint
from pywaclient.endpoints.chronicles import ChronicleCrudEndpoint
from pywaclient.endpoints.histories import HistoryCrudEndpoint
from pywaclient.endpoints.images import ImageCrudEndpoint
from pywaclient.endpoints.manuscripts import ManuscriptCrudEndpoint
from pywaclient.endpoints.map_marker_types import MapMarkerTypeCrudEndpoint
from pywaclient.endpoints.maps import MapCrudEndpoint
from pywaclient.endpoints.notebooks import NotebookCrudEndpoint
from pywaclient.endpoints.rpg_system import RpgSystemCrudEndpoint
from pywaclient.endpoints.secrets import SecretCrudEndpoint
from pywaclient.endpoints.subscriber_groups import SubscriberGroupCrudEndpoint
from pywaclient.endpoints.timelines import TimelineCrudEndpoint
from pywaclient.endpoints.users import UserCrudEndpoint
from pywaclient.endpoints.variables import VariableCollectionCrudEndpoint
from pywaclient.endpoints.worlds import WorldCrudEndpoint


class BoromirApiClient:

    def __init__(self,
                 name: str,
                 url: str,
                 version: str,
                 application_key: str,
                 authentication_token: str,
                 ):
        self.headers = {
            'x-auth-token': authentication_token,
            'x-application-key': application_key,
            'Accept': 'application/json',
            'User-Agent': f'{name} ({url}, {version})'
        }
        self.headers_post = self.headers.copy()
        self.headers_post['Content-type'] = 'application/json'
        self.base_url = 'https://www.worldanvil.com/api/external/boromir/'
        self.block = BlockCrudEndpoint(self)
        self.block_folder = BlockFolderCrudEndpoint(self)
        self.article = ArticleCrudEndpoint(self)
        self.image = ImageCrudEndpoint(self)
        self.manuscript = ManuscriptCrudEndpoint(self)
        self.user = UserCrudEndpoint(self)
        self.secret = SecretCrudEndpoint(self)
        self.world = WorldCrudEndpoint(self)
        self.category = CategoryCrudEndpoint(self)
        self.variable_collection = VariableCollectionCrudEndpoint(self)
        self.rpg_system = RpgSystemCrudEndpoint(self)
        self.subscriber_group = SubscriberGroupCrudEndpoint(self)
        self.map = MapCrudEndpoint(self)
        self.map_marker_types = MapMarkerTypeCrudEndpoint(self)
        self.history = HistoryCrudEndpoint(self)
        self.timeline = TimelineCrudEndpoint(self)
        self.canvas = CanvasCrudEndpoint(self)
        self.chronicle = ChronicleCrudEndpoint(self)
        self.block_template = BlockTemplateCrudEndpoint(self)
        self.notebook = NotebookCrudEndpoint(self)