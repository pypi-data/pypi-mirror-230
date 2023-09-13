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

from typing import Dict, Any, Iterable

from pywaclient.endpoints import CrudEndpoint


class WorldCrudEndpoint(CrudEndpoint):

    def __init__(self, client: 'BoromirApiClient'):
        super().__init__(client, 'world')
        self.path_articles = f'{self.path}/articles'
        self.path_categories = f'{self.path}/categories'
        self.path_block_folders = f'{self.path}/blockfolders'
        self.path_variable_collections = f'{self.path}/variablecollections'
        self.path_subscriber_groups = f'{self.path}/subscribergroups'
        self.path_secrets = f'{self.path}/secrets'
        self.path_manuscripts = f'{self.path}/manuscripts'
        self.path_maps = f'{self.path}/maps'
        self.path_images = f'{self.path}/images'
        self.path_histories = f'{self.path}/histories'
        self.path_timelines = f'{self.path}/timelines'
        self.path_chronicles = f'{self.path}/chronicles'
        self.path_canvases = f'{self.path}/canvases'
        self.path_blocks = f'{self.path}/blocks'

    def articles(self, world_id: str, category_id: str, complete: bool = True, limit: int = 50, offset: int = 0) -> Iterable[Dict[str, Any]]:
        """
        List all articles by a world and category given, filtered with a limit of entities shown and an offset.

        :param world_id:    The id of the world the articles should be returned from.
        :param category_id: The id of the category to return the articles from. To get articles without a category set
                            this value to -1. This does not return articles that have a parent article instead of a
                            category.
        :param complete     Ignore limit and offset and return all the articles as an iterable. Will fetch a new batch
                            every 50 articles.
        :param limit:       Determines how many articles are returned. Value between 1 and 50.
        :param offset:      Determines the offset at which articles are returned. Has to be a positive integer.
        :return:
        """
        if complete:
            return self._scroll_collection(self.path_articles, {'id': world_id}, 'entities', 'category', category_id)
        return self._post_request(self.path_articles,
                                  {'id': world_id},
                                  {'limit': limit, 'offset': offset, 'category': {'id': category_id}})['entities']

    def categories(self, world_id: str, complete: bool = True, limit: int = 50, offset: int = 0) -> Iterable[
        Dict[str, Any]]:
        """
        List all categories by a world given, filtered with a limit of entities shown and an offset.

        :param world_id:    The id of the world the folders should be returned from.
        :param complete:    Return the entire list of entities as a list. Only loads 50 categories at a time.
        :param limit:       Determines how many folders are returned. Value between 1 and 50.
        :param offset:      Determines the offset at which folders are returned. Has to be a positive integer.
        :return:
        """
        if complete:
            return self._scroll_collection(self.path_categories, {'id': world_id}, 'entities')
        return self._post_request(self.path_categories,
                                  {'id': world_id},
                                  {'limit': limit, 'offset': offset})['entities']

    def statblock_folders(self, world_id: str, complete: bool = True, limit: int = 50, offset: int = 0) -> Iterable[
        Dict[str, Any]]:
        """
        List all statblock folders of a specific world.

        :param world_id:    The id of the world
        :param complete:    Return the entire list of entities as an iterable. This ignores limit and offset when
                            set to true.
        :param limit:       The number of entries returned per request. 1 <= limit <= 50
        :param offset:      The offset in the list of entries to return from. offset >=
        :return:            An iterable of statblock folder entities.
        """
        assert 1 <= limit <= 50
        assert offset >= 0
        if complete:
            return self._scroll_collection(self.path_block_folders, {'id': world_id}, 'entities')
        return self._post_request(self.path_block_folders,
                                  {'id': world_id},
                                  {'limit': limit, 'offset': offset})['entities']

    def variable_collections(self, world_id: str, complete: bool = True, limit: int = 50, offset: int = 0) -> Iterable[
        Dict[str, Any]]:
        """
        List all variable collections of a specific world.

        :param world_id:    The id of the world
        :param complete:    Return the entire list of entities as an iterable. This ignores limit and offset when
                            set to true.
        :param limit:       The number of entries returned per request. 1 <= limit <= 50
        :param offset:      The offset in the list of entries to return from. offset >=
        :return:            An iterable of variable collection entities.
        """
        assert 1 <= limit <= 50
        assert offset >= 0
        if complete:
            return self._scroll_collection(self.path_variable_collections, {'id': world_id}, 'entities')
        return self._post_request(self.path_variable_collections,
                                  {'id': world_id},
                                  {'limit': limit, 'offset': offset})['entities']

    def subscriber_groups(self, world_id: str, complete: bool = True, limit: int = 50, offset: int = 0) -> Iterable[
        Dict[str, Any]]:
        """
        List all subscriber groups of a specific world.

        :param world_id:    The id of the world
        :param complete:    Return the entire list of entities as an iterable. This ignores limit and offset when
                            set to true.
        :param limit:       The number of entries returned per request. 1 <= limit <= 50
        :param offset:      The offset in the list of entries to return from. offset >=
        :return:            An iterable of subscriber group entities.
        """
        assert 1 <= limit <= 50
        assert offset >= 0
        if complete:
            return self._scroll_collection(self.path_subscriber_groups, {'id': world_id}, 'entities')
        return self._post_request(self.path_subscriber_groups,
                                  {'id': world_id},
                                  {'limit': limit, 'offset': offset})['entities']

    def secrets(self, world_id: str, complete: bool = True, limit: int = 50, offset: int = 0) -> Iterable[
        Dict[str, Any]]:
        """
        List all secrets of a specific world.

        :param world_id:    The id of the world
        :param complete:    Return the entire list of entities as an iterable. This ignores limit and offset when
                            set to true.
        :param limit:       The number of entries returned per request. 1 <= limit <= 50
        :param offset:      The offset in the list of entries to return from. offset >=
        :return:            An iterable of secret entities.
        """
        assert 1 <= limit <= 50
        assert offset >= 0
        if complete:
            return self._scroll_collection(self.path_secrets, {'id': world_id}, 'entities')
        return self._post_request(self.path_secrets,
                                  {'id': world_id},
                                  {'limit': limit, 'offset': offset})['entities']

    def manuscripts(self, world_id: str, complete: bool = True, limit: int = 50, offset: int = 0) -> Iterable[
        Dict[str, Any]]:
        """
        List all manuscripts of a specific world.

        :param world_id:    The id of the world
        :param complete:    Return the entire list of entities as an iterable. This ignores limit and offset when
                            set to true.
        :param limit:       The number of entries returned per request. 1 <= limit <= 50
        :param offset:      The offset in the list of entries to return from. offset >=
        :return:            An iterable of manuscript entities.
        """
        assert 1 <= limit <= 50
        assert offset >= 0
        if complete:
            return self._scroll_collection(self.path_manuscripts, {'id': world_id}, 'entities')
        return self._post_request(self.path_manuscripts,
                                  {'id': world_id},
                                  {'limit': limit, 'offset': offset})['entities']

    def maps(self, world_id: str, complete: bool = True, limit: int = 50, offset: int = 0) -> Iterable[
        Dict[str, Any]]:
        """
        List all maps of a specific world.

        :param world_id:    The id of the world
        :param complete:    Return the entire list of entities as an iterable. This ignores limit and offset when
                            set to true.
        :param limit:       The number of entries returned per request. 1 <= limit <= 50
        :param offset:      The offset in the list of entries to return from. offset >=
        :return:            An iterable of map entities.
        """
        assert 1 <= limit <= 50
        assert offset >= 0
        if complete:
            return self._scroll_collection(self.path_maps, {'id': world_id}, 'entities')
        return self._post_request(self.path_maps,
                                  {'id': world_id},
                                  {'limit': limit, 'offset': offset})['entities']

    def images(self, world_id: str, complete: bool = True, limit: int = 50, offset: int = 0) -> Iterable[
        Dict[str, Any]]:
        """
        List all images of a specific world.

        :param world_id:    The id of the world
        :param complete:    Return the entire list of entities as an iterable. This ignores limit and offset when
                            set to true.
        :param limit:       The number of entries returned per request. 1 <= limit <= 50
        :param offset:      The offset in the list of entries to return from. offset >=
        :return:            An iterable of image entities.
        """
        assert 1 <= limit <= 50
        assert offset >= 0
        if complete:
            return self._scroll_collection(self.path_images, {'id': world_id}, 'entities')
        return self._post_request(self.path_images,
                                  {'id': world_id},
                                  {'limit': limit, 'offset': offset})['entities']

    def histories(self, world_id: str, complete: bool = True, limit: int = 50, offset: int = 0) -> Iterable[
        Dict[str, Any]]:
        """
        List all histories of a specific world.

        :param world_id:    The id of the world
        :param complete:    Return the entire list of entities as an iterable. This ignores limit and offset when
                            set to true.
        :param limit:       The number of entries returned per request. 1 <= limit <= 50
        :param offset:      The offset in the list of entries to return from. offset >=
        :return:            An iterable of history entities.
        """
        assert 1 <= limit <= 50
        assert offset >= 0
        if complete:
            return self._scroll_collection(self.path_histories, {'id': world_id}, 'entities')
        return self._post_request(self.path_histories,
                                  {'id': world_id},
                                  {'limit': limit, 'offset': offset})['entities']

    def timelines(self, world_id: str, complete: bool = True, limit: int = 50, offset: int = 0) -> Iterable[
        Dict[str, Any]]:
        """
        List all timelines of a specific world.

        :param world_id:    The id of the world
        :param complete:    Return the entire list of entities as an iterable. This ignores limit and offset when
                            set to true.
        :param limit:       The number of entries returned per request. 1 <= limit <= 50
        :param offset:      The offset in the list of entries to return from. offset >=
        :return:            An iterable of timeline entities.
        """
        assert 1 <= limit <= 50
        assert offset >= 0
        if complete:
            return self._scroll_collection(self.path_timelines, {'id': world_id}, 'entities')
        return self._post_request(self.path_timelines,
                                  {'id': world_id},
                                  {'limit': limit, 'offset': offset})['entities']

    def chronicles(self, world_id: str, complete: bool = True, limit: int = 50, offset: int = 0) -> Iterable[
        Dict[str, Any]]:
        """
        List all chronicles of a specific world.

        :param world_id:    The id of the world
        :param complete:    Return the entire list of entities as an iterable. This ignores limit and offset when
                            set to true.
        :param limit:       The number of entries returned per request. 1 <= limit <= 50
        :param offset:      The offset in the list of entries to return from. offset >=
        :return:            An iterable of chronicle entities.
        """
        assert 1 <= limit <= 50
        assert offset >= 0
        if complete:
            return self._scroll_collection(self.path_chronicles, {'id': world_id}, 'entities')
        return self._post_request(self.path_chronicles,
                                  {'id': world_id},
                                  {'limit': limit, 'offset': offset})['entities']

    def canvases(self, world_id: str, complete: bool = True, limit: int = 50, offset: int = 0) -> Iterable[
        Dict[str, Any]]:
        """
        List all canvases of a specific world.

        :param world_id:    The id of the world
        :param complete:    Return the entire list of entities as an iterable. This ignores limit and offset when
                            set to true.
        :param limit:       The number of entries returned per request. 1 <= limit <= 50
        :param offset:      The offset in the list of entries to return from. offset >=
        :return:            An iterable of canvas entities.
        """
        assert 1 <= limit <= 50
        assert offset >= 0
        if complete:
            return self._scroll_collection(self.path_canvases, {'id': world_id}, 'entities')
        return self._post_request(self.path_canvases,
                                  {'id': world_id},
                                  {'limit': limit, 'offset': offset})['entities']

    def blocks(self, world_id: str, complete: bool = True, limit: int = 50, offset: int = 0) -> Iterable[Dict[str, Any]]:
        """
        Retrieve a list of blocks from a world.

        :param world_id:    The id of the world the blocks should be returned from.
        :param complete:    Returns all the folders as an iterable.
        :param limit:       Determines how many articles are returned. Value between 1 and 50.
        :param offset:      Determines the offset at which articles are returned. Has to be a positive integer.
        :return:
        """
        if complete:
            return self._scroll_collection(self.path_blocks, {'id': world_id}, 'entities')
        return self._post_request(self.path_blocks,
                                  {'id': world_id},
                                  {'limit': limit, 'offset': offset})['entities']

