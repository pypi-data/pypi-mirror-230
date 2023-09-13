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
import logging
from typing import Dict, Any, Iterable

import requests
from requests import RequestException, Response

from pywaclient.exceptions import AccessForbidden, ResourceNotFound, InternalServerException, \
    UnexpectedStatusException, ConnectionException, UnprocessableDataProvided, FailedRequest, UnauthorizedRequest


def download_binary(url: str, chunk_size: int = 8192) -> Iterable[bytes]:
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        for chunk in r.iter_content(chunk_size=chunk_size):
            yield chunk

def _parse_response(path: str, response: Response, params: Dict[str, Any], content: Dict[str, Any]) -> Dict[str, Any]:
    if response.ok:
        data = response.json()
        if 'success' not in data:
            raise UnexpectedStatusException(response.status_code, 'Response contained no success flag.', path, params, content)
        if data['success']:
            return data
        else:
            raise FailedRequest(response.status_code, path, data['error'], data, params, content)
    elif response.status_code == 401:
        raise UnauthorizedRequest(path, params, content)
    elif response.status_code == 403:
        raise AccessForbidden(path, params, content)
    elif response.status_code == 404:
        raise ResourceNotFound(path, params, content)
    elif response.status_code == 422:
        raise UnprocessableDataProvided(path, response.json(), params, content)
    elif response.status_code == 500:
        raise InternalServerException(500, path, params, content)
    else:
        raise UnexpectedStatusException(response.status_code, response.reason, path, params, content)


class BasicEndpoint:

    def __init__(self, client: 'AragornApiClient', base_path: str):
        self.client = client
        self.path = base_path

    def _get_request(self, path: str, params: Dict[str, str]) -> Dict[str, Any]:
        try:
            response = requests.get(self.client.base_url + path, params=params, headers=self.client.headers)
            return _parse_response(path, response, params, {})
        except RequestException as err:
            raise ConnectionException(str(err))

    def _put_request(self, path: str, content: Dict[str, Any]) -> Dict[str, Any]:
        try:
            response = requests.put(self.client.base_url + path, json=content, headers=self.client.headers_post)
            return _parse_response(path, response, {}, content)
        except RequestException as err:
            raise ConnectionException(str(err))

    def _patch_request(self, path: str, params: Dict[str, str], content: Dict[str, Any]) -> Dict[str, Any]:
        try:
            response = requests.patch(self.client.base_url + path, params=params, json=content,
                                      headers=self.client.headers_post)
            return _parse_response(path, response, params, content)
        except RequestException as err:
            raise ConnectionException(str(err))

    def _post_request(self, path: str, params: Dict[str, str], content: Dict[str, Any]) -> Dict[str, Any]:
        try:
            response = requests.post(self.client.base_url + path, params=params, json=content,
                                     headers=self.client.headers_post)
            return _parse_response(path, response, params, content)
        except RequestException as err:
            raise ConnectionException(str(err))

    def _delete_request(self, path: str, params: Dict[str, str]):
        try:
            response = requests.delete(self.client.base_url + path,
                                       params=params,
                                       headers=self.client.headers)
            return _parse_response(path, response, params, {})
        except RequestException as err:
            raise ConnectionException(str(err))


    def _scroll_collection(self, path: str, params: Dict[str, str], collection_tag: str, parentName: str = '', parentId: str = '') -> Iterable[Dict[str, Any]]:
        limit = 50
        offset = 0
        if parentName != '':
            content = {'limit': limit, 'offset': offset, parentName: {'id': parentId}}
        else:
            content = {'limit': limit, 'offset': offset}
        collection = self._post_request(path, params, content)
        if collection['success']:
            items = collection[collection_tag]
            while len(items) > 0:
                for item in items:
                    yield item
                offset = offset + limit
                content['offset'] = offset
                collection = self._post_request(path, params, content)
                items = collection[collection_tag]

    def get(self, identifier: str, granularity: int) -> Dict[str, Any]:
        """Retrieve the metadata of the resources. Use the granularity parameter to determine the amount of information
        returned by the api.

        :param identifier:  The id of the resource.
        :param granularity: The granularity of the response. -1: reference only, 0: default, 1: full, 2: extended, 3: special
        :return:            The metadata of the resource.
        """
        return self._get_request(self.path, {'id': identifier, 'granularity': str(granularity)})


class CrudEndpoint(BasicEndpoint):

    def __init__(self, client: 'AragornApiClient', base_path: str):
        super().__init__(client, base_path)

    def put(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Create the resource.

        :param content:     The content of the resource. Including required fields.
        :return:            The reference of the created resource.
        """
        return self._put_request(self.path, content)

    def patch(self, identifier: str, content: Dict[str, Any]) -> Dict[str, Any]:
        """Update the resource with the given id. The content should contain the fields that should be overwritten.

        :param identifier:  The id of the resource to be updated.
        :param content:     The fields that should be overwritten.
        :return:            The reference of the updated resource.
        """
        return self._patch_request(self.path, {'id': identifier}, content)

    def delete(self, identifier: str):
        """Delete the resource with the given id.

        :param identifier:  The id of the resource to be deleted.
        """
        self._delete_request(self.path, {'id': identifier})
