from typing import Dict, Any


class WorldAnvilClientException(Exception):
    """Base exception to the library."""


class WorldAnvilServerException(WorldAnvilClientException):
    """Exceptions returned by the server for requests made."""

    def __init__(self, status: int, message: str, summary: str = "", path: str = None, params: Dict[str, Any] = None, content: Dict[str, Any] = None):
        self.status = status
        self.message = message
        self.summary = summary
        self.path = path
        self.content = content
        self.params = params


class ConnectionException(WorldAnvilServerException):
    """Was unable to connect to World Anvil for some reason."""

    def __init__(self, message: str):
        super().__init__(503, message)


class UnexpectedStatusException(WorldAnvilServerException):
    """An unexpected status exception occurred."""

    def __init__(self, status: int, message: str, path: str, params: Dict[str, Any], content: Dict[str, Any]):
        super().__init__(status, message, "", path, params, content)


class InternalServerException(WorldAnvilServerException):
    """Internal Server Error in World Anvil Response."""

    def __init__(self, status: int, path: str, params: Dict[str, Any], content: Dict[str, Any]):
        super().__init__(status, 'World Anvil was unable to process this request.', "", path, params, content)


class UnauthorizedRequest(WorldAnvilServerException):
    """The user is not authorized to access the requested resource. This can happen if no authentication token or application key was provided or the provided token or key are not valid."""

    def __init__(self, path: str, params: Dict[str, Any], content: Dict[str, Any]):
        super().__init__(401, "Unauthorized.", "Either no authentication token or application key was provided or the provided token or key are not valid.", path, params, content)

class AccessForbidden(WorldAnvilServerException):
    """The user does not have permissions for the requested resources."""

    def __init__(self, path: str, params: Dict[str, Any], content: Dict[str, Any]):
        super().__init__(403, "Permission denied.", "The authentication token does not allow access to the requested resource.", path, params, content)


class ResourceNotFound(WorldAnvilServerException):
    """The requested resource does not exist or was moved."""

    def __init__(self, path: str, params: Dict[str, Any], content: Dict[str, Any]):
        super().__init__(404, "Requested resource was not found.", "", path, params, content)


class UnprocessableDataProvided(WorldAnvilServerException):
    """The request could not be processed."""

    def __init__(self, path: str, data: Dict[str, Any], params: Dict[str, Any], content: Dict[str, Any]):
        if 'status' in data:
            super().__init__(422, "Unprocessable data provided", data['error']['summary'], path, params, content)
            self.error_tracestack = data['error']['traceStack']
        else:
            super().__init__(422, "Unprocessable data provided", data['error'], path, params, content)
            self.error_tracestack = data['trace']

class FailedRequest(WorldAnvilServerException):
    """Status code indicated success, but request failed."""

    def __init__(self, status: int, path: str, message: str, response: Dict[str, Any], params: Dict[str, Any], content: Dict[str, Any]):
        super().__init__(status, message, path, params, content)
        self.response = response