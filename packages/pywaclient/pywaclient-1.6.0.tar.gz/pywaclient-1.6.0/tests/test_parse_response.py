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
from unittest.mock import Mock

import pytest
from hypothesis import given, strategies as st, settings, example

from pywaclient.endpoints import _parse_response
from pywaclient.exceptions import AccessForbidden, ResourceNotFound, InternalServerException, \
    UnexpectedStatusException, ConnectionException, UnprocessableDataProvided, FailedRequest

key_values = [
    'success',
    'id',
    'title',
    'slug',
    'excerpt',
    'content',
    'templateType',
]

def is_status_ok(status_code):
    return 199 < status_code < 400

def add_error(x: dict):
    x['error'] = st.text()
    return x
@given(
    path=st.text(),
    status_code=st.integers(min_value=200, max_value=599),
    content=st.dictionaries(
        keys=st.sampled_from(key_values),
        values=st.text()).map(lambda x: st.fixed_dictionaries({'success': st.booleans()}).map(lambda fixed_dict: {**fixed_dict, **x}))
)
@settings(max_examples=1000)
@example(path='', status_code=200, content={'success': True})
def test_parse_response(path, status_code, content):
    response = Mock(status_code=status_code, ok=is_status_ok(status_code), json=Mock(return_value=content))
    params = {'param1': 'value1', 'param2': 'value2'}

    if 'success' not in content:
        with pytest.raises(UnexpectedStatusException):
            _parse_response(path, response, params, content)
    if is_status_ok(status_code) and content.get('success', False):
        assert _parse_response(path, response, params, content) == content
    elif is_status_ok(status_code) and not content.get('success', False):
        with pytest.raises(FailedRequest):
            _parse_response(path, response, params, content)
    elif status_code == 401 or status_code == 403:
        with pytest.raises(AccessForbidden):
            _parse_response(path, response, params, content)
    elif status_code == 404:
        with pytest.raises(ResourceNotFound):
            _parse_response(path, response, params, content)
    elif status_code == 422:
        with pytest.raises(UnprocessableDataProvided):
            _parse_response(path, response, params, content)
    elif status_code == 500:
        with pytest.raises(InternalServerException):
            _parse_response(path, response, params, content)
    else:
        with pytest.raises(UnexpectedStatusException):
            _parse_response(path, response, params, content)
