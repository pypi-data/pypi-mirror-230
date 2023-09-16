"""
Service class to handle low-level communication.
"""

import asyncio
import json
import typing
from abc import ABC, abstractmethod
from dataclasses import dataclass
from types import TracebackType
from typing import Any, Callable, Dict, Optional, Union

import httpx

from aidkit_client.authenticator import AuthenticatorService
from aidkit_client.exceptions import (
    AidkitClientError,
    AuthenticationError,
    ResourceWithNameNotFoundError,
)

API_VERSION = "1.0"


@dataclass
class Response:
    """
    Response of an aidkit server.
    """

    status_code: int
    body: Union[Dict[str, Any], str]

    @property
    def is_success(self) -> bool:
        """
        Return whether the request prompting the response was handled
        successfully.

        :return: True if the aidkit server indicated success, False otherwise.
        """
        return self.status_code in (200, 201, 204)

    @property
    def is_not_found(self) -> bool:
        """
        Return whether a resource was not found.

        :return: True if the aidkit server indicated that a resource was not
            found, False otherwise.
        """
        return self.status_code == 404

    @property
    def is_bad(self) -> bool:
        """
        Return whether the request prompting the response was deemed a bad
        request by the server.

        :return: True if the server returned a "bad request" error code, False
            otherwise.
        """
        return self.status_code == 400

    def body_dict_or_error(self, error_message: str) -> dict:
        """
        Return the body dictionary if the response indicates success and is a
        dictionary, raise the appropriate error otherwise.

        :param error_message: Error message to prepend to the raised error if
            an error is raised. Must contain relevant context.
        :raises AuthenticationError: If the server returned a 401 status code.
        :raises ResourceWithNameNotFoundError: If the server returned a 404
            status code.
        :raises AidkitClientError: If some other error occured or if the server did
            not return a dictionary.
        :return: Body of the response.
        """
        if self.status_code == 401:
            if self.body == "Invalid audience" or (
                isinstance(self.body, str)
                and self.body.startswith("Unable to find a signing key that matches: ")
            ):
                raise AuthenticationError("JWT token is not usable for this domain.")
            if self.body == "Signature has expired":
                raise AuthenticationError("Used JWT token is expired.")
            raise AuthenticationError(f"Server response: '{self.body}'")
        if self.is_not_found:
            raise ResourceWithNameNotFoundError(
                error_message,
                f"Server responded with error code {self.status_code} and message {self.body}.",
            )
        if not self.is_success:
            raise AidkitClientError(
                error_message,
                f"Server responded with error code {self.status_code} and message '{self.body}'",
            )
        if not isinstance(self.body, dict):
            raise AidkitClientError(
                "Server did not respond with a dictionary, " f"but with the string '{self.body}'"
            )
        return self.body


class HTTPService(ABC):
    """
    Abstract HTTP service to use REST methods.
    """

    @abstractmethod
    async def get(
        self,
        path: str,
        parameters: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, Any]] = None,
    ) -> Response:
        """
        Get a resource on the server.

        :param headers: Headers for httpx.AsyncClient
        :param path: Path of the resource to get.
        :param parameters: Parameters to pass to the server.
        :returns: Response of the server.
        """

    @abstractmethod
    async def post_json(
        self,
        path: str,
        parameters: Optional[Dict[str, Any]] = None,
        body: Optional[dict] = None,
        headers: Optional[Dict[str, Any]] = None,
    ) -> Response:
        """
        Post JSON data to the server.

        :param headers: Headers for httpx.AsyncClient
        :param path: Path of the resource to be posted.
        :param parameters: Parameters to be passed to the server.
        :param parameters: Parameters to be passed to the server.
        :param body: JSON body to be posted to the server.
        :returns: Response of the server.
        """

    @abstractmethod
    async def post_multipart_data(
        self,
        path: str,
        data: Optional[dict] = None,
        files: Optional[dict] = None,
        headers: Optional[Dict[str, Any]] = None,
    ) -> Response:
        """
        Post multipart data to the server.

        :param headers: Headers for httpx.AsyncClient
        :param path: Path of the resource to be posted.
        :param data: Data to be uploaded to the server.
        :param files: Files to be uploaded to the server.
        :returns: Response of the server.
        """

    @abstractmethod
    async def patch(
        self,
        path: str,
        parameters: Optional[Dict[str, Any]] = None,
        body: Optional[dict] = None,
        headers: Optional[Dict[str, Any]] = None,
    ) -> Response:
        """
        Patch a resource on the server.

        :param headers: Headers for httpx.AsyncClient
        :param path: Path of the resource to be patched.
        :param parameters: Parameters to pass to the server.
        :param body: JSON body of the patch request.
        :returns: Response of the server.
        """

    @abstractmethod
    async def delete(
        self,
        path: str,
        parameters: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, Any]] = None,
    ) -> Response:
        """
        Delete a resource on the server.

        :param headers: Headers for httpx.AsyncClient
        :param path: Path of the resource to be deleted.
        :param parameters: Parameters to pass to the server.
        :returns: Response of the server.
        """

    @abstractmethod
    async def get_from_cdn(self, url: str, headers: Optional[Dict[str, Any]] = None) -> Response:
        """
        Get a file from the content delivery network.

        :param headers: Headers for httpx.AsyncClient
        :param url: url to access
        :returns: Response of the server.
        """

    @abstractmethod
    async def __aenter__(self) -> "HTTPService":
        """
        Enter the context to use the aidkit api within.
        """

    @abstractmethod
    async def __aexit__(
        self,
        exc_type: Optional[typing.Type[BaseException]] = None,
        exc_value: Optional[BaseException] = None,
        traceback: Optional[TracebackType] = None,
    ) -> None:
        """
        Exit the context of the underlying HTTPX client.

        :param exc_type: Exception type, if an exception is the reason to exit
            the context.
        :param exc_value: Exception value, if an exception is the reason to exit
            the context.
        :param traceback: Traceback, if an exception is the reason to exit
            the context.
            the context
        :param exc_value: Exception value, if an exception is the reason to exit
            the context
        :param traceback: Traceback, if an exception is the reason to exit
            the context
        """


class AidkitApi(HTTPService):
    """
    HTTP Service to be used to communicate with an aidkit server.
    """

    client: httpx.AsyncClient

    def __init__(self, client: httpx.AsyncClient) -> None:
        """
        Create a new instance configured with a base URL and a JWT auth token.

        :param client: HTTPX Async Client to use
        """
        self.client = client

    async def __aenter__(self) -> "AidkitApi":
        """
        Enter the context to use the aidkit api within.

        :return: AidkitApi this method is called on.
        """
        await self.client.__aenter__()
        return self

    async def __aexit__(
        self,
        exc_type: Optional[typing.Type[BaseException]] = None,
        exc_value: Optional[BaseException] = None,
        traceback: Optional[TracebackType] = None,
    ) -> None:
        """
        Exit the context of the underlying HTTPX client.

        :param exc_type: Exception type, if an exception is the reason to exit
            the context.
        :param exc_value: Exception value, if an exception is the reason to exit
            the context.
        :param traceback: Traceback, if an exception is the reason to exit
            the context.
            the context
        :param exc_value: Exception value, if an exception is the reason to exit
            the context
        :param traceback: Traceback, if an exception is the reason to exit
            the context
        """
        await self.client.__aexit__(exc_type=exc_type, exc_value=exc_value, traceback=traceback)

    async def get(
        self,
        path: str,
        parameters: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, Any]] = None,
    ) -> Response:
        """
        Get a resource on the server.

        :param path: Path of the resource to get.
        :param parameters: Parameters to pass to the server.
        :param headers: Headers for httpx.AsyncClient
        :returns: Response of the server.
        """
        response = await self.client.get(url=path, params=parameters, headers=headers)
        return self._to_aidkit_response(response)

    async def get_from_cdn(self, url: str, headers: Optional[Dict[str, Any]] = None) -> Response:
        """
        Get a file from the content delivery network.

        :param url: url to access
        :param headers: Headers for httpx.AsyncClient
        :returns: Response of the server.
        """
        res = await self.client.get(url=url, headers=headers)

        return Response(
            status_code=res.status_code,
            body={"content": res.content},
        )

    async def post_json(
        self,
        path: str,
        parameters: Optional[Dict[str, Any]] = None,
        body: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, Any]] = None,
    ) -> Response:
        """
        Post JSON data to the server.

        :param path: Path of the resource to be posted.
        :param parameters: Parameters to be passed to the server.
        :param body: JSON body to be posted to the server.
        :param headers: Headers for httpx.AsyncClient
        :returns: Response of the server.
        """
        response = await self.client.post(url=path, params=parameters, json=body, headers=headers)
        return self._to_aidkit_response(response)

    async def post_multipart_data(
        self,
        path: str,
        data: Optional[dict] = None,
        files: Optional[dict] = None,
        headers: Optional[Dict[str, Any]] = None,
    ) -> Response:
        """
        Post multipart data to the server.

        :param path: Path of the resource to be posted.
        :param data: Data to be uploaded to the server.
        :param files: Files to be uploaded to the server.
        :param headers: Headers for httpx.AsyncClient
        :returns: Response of the server.
        """
        response = await self.client.post(url=path, headers=headers, data=data, files=files)
        return self._to_aidkit_response(response)

    async def patch(
        self,
        path: str,
        parameters: Optional[Dict[str, Any]] = None,
        body: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, Any]] = None,
    ) -> Response:
        """
        Patch a resource on the server.

        :param path: Path of the resource to be patched.
        :param parameters: Parameters to pass to the server.
        :param body: JSON body of the patch request.
        :param headers: Headers for httpx.AsyncClient
        :returns: Response of the server.
        """
        response = await self.client.patch(url=path, params=parameters, json=body, headers=headers)
        return self._to_aidkit_response(response)

    async def delete(
        self,
        path: str,
        parameters: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, Any]] = None,
    ) -> Response:
        """
        Delete a resource on the server.

        :param path: Path of the resource to be deleted.
        :param parameters: Parameters to pass to the server.
        :param headers: Headers for httpx.AsyncClient
        :returns: Response of the server.
        """
        response = await self.client.delete(url=path, params=parameters, headers=headers)
        return self._to_aidkit_response(response)

    @classmethod
    def _to_aidkit_response(cls, res: httpx.Response) -> Response:
        try:
            return Response(status_code=res.status_code, body=res.json())
        except json.decoder.JSONDecodeError:
            return Response(status_code=res.status_code, body={"not_json_decodable": res.content})


class AuthorizingHTTPService(HTTPService):
    """
    HTTP Service to be used to communicate with an aidkit server.
    """

    _internal_http_service: HTTPService
    _authenticator_service: AuthenticatorService
    jwt_token: Union[str, asyncio.Task]

    def __init__(
        self,
        _internal_http_service: HTTPService,
        _authenticator_service: AuthenticatorService,
        auth_secret: str,
    ) -> None:
        """
        Create a new instance configured with a base URL and a JWT auth token.

        :param auth_secret: Auth secret for exchanging to JWT
        :param _authenticator_service: authenticator service
        :param _internal_http_service: The AidkitApi service to call
        """
        self._internal_http_service = _internal_http_service
        self.auth_url = self._construct_auth_url_from_application_id(auth_secret)
        self.auth_secret = auth_secret
        self._authenticator_service = _authenticator_service
        self.jwt_token = ""  # noqa: S105

    async def __aenter__(self) -> "HTTPService":
        """
        Enter the context to use the aidkit api within.

        :return: HTTPService this method is called on.
        """
        result = await self._internal_http_service.__aenter__()
        return result

    async def __aexit__(
        self,
        exc_type: Optional[typing.Type[BaseException]] = None,
        exc_value: Optional[BaseException] = None,
        traceback: Optional[TracebackType] = None,
    ) -> None:
        """
        Exit the context of the underlying HTTPX client.

        :param exc_type: Exception type, if an exception is the reason to exit
            the context.
        :param exc_value: Exception value, if an exception is the reason to exit
            the context.
        :param traceback: Traceback, if an exception is the reason to exit
            the context.
            the context
        :param exc_value: Exception value, if an exception is the reason to exit
            the context
        :param traceback: Traceback, if an exception is the reason to exit
            the context
        """
        await self._internal_http_service.__aexit__(
            exc_type=exc_type, exc_value=exc_value, traceback=traceback
        )

    async def with_renew_token_and_retry(self, func: Callable) -> Response:
        """
        This will call the passed function, and check if the response is a 401
        with 'Signature has expired' as message. If this is the case, the JWT
        token will be renewed and the call will be repeated. In both cases the
        response is the response of the Callable.

        :param func: function to call
        :returns: function Response, identical to the response of the param func
        """
        retry_request = False
        retry_on_message = "Signature has expired"
        result = await func()

        if (
            result.status_code == 401
            and isinstance(result.body, str)
            and result.body == retry_on_message
        ):
            retry_request = True

        if (
            result.status_code == 401
            and isinstance(result.body, dict)
            and "content" in result.body
            and isinstance(result.body["content"], bytes)
            and result.body["content"].decode("utf-8") == retry_on_message
        ):
            retry_request = True

        if retry_request:
            self.jwt_token = await self._authenticator_service.resolve_secret_to_access_token(
                self.auth_secret, self.auth_url
            )
            result = await func()

        return result

    async def get(
        self,
        path: str,
        parameters: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, Any]] = None,
    ) -> Response:
        """
        Get a resource on the server.

        :param headers: Headers for httpx.AsyncClient
        :param path: Path of the resource to get.
        :param parameters: Parameters to pass to the server.
        :returns: Response of the server.
        """

        async def perform() -> Response:
            return await self._internal_http_service.get(
                path=path, parameters=parameters, headers=await self._get_headers()
            )

        return await self.with_renew_token_and_retry(func=perform)

    async def get_from_cdn(self, url: str, headers: Optional[Dict[str, Any]] = None) -> Response:
        """
        Get a file from the content delivery network.

        :param headers: Headers for httpx.AsyncClient
        :param url: url to access
        :returns: Response of the server.
        """

        async def perform() -> Response:
            return await self._internal_http_service.get_from_cdn(
                url=url, headers=await self._get_headers()
            )

        return await self.with_renew_token_and_retry(func=perform)

    async def post_json(
        self,
        path: str,
        parameters: Optional[Dict[str, Any]] = None,
        body: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, Any]] = None,
    ) -> Response:
        """
        Post JSON data to the server.

        :param headers: Headers for httpx.AsyncClient
        :param path: Path of the resource to be posted.
        :param parameters: Parameters to be passed to the server.
        :param body: JSON body to be posted to the server.
        :returns: Response of the server.
        """

        async def perform() -> Response:
            return await self._internal_http_service.post_json(
                path=path, headers=await self._get_headers(), parameters=parameters, body=body
            )

        return await self.with_renew_token_and_retry(func=perform)

    async def post_multipart_data(
        self,
        path: str,
        data: Optional[dict] = None,
        files: Optional[dict] = None,
        headers: Optional[Dict[str, Any]] = None,
    ) -> Response:
        """
        Post multipart data to the server.

        :param headers: Headers for httpx.AsyncClient
        :param path: Path of the resource to be posted.
        :param data: Data to be uploaded to the server.
        :param files: Files to be uploaded to the server.
        :returns: Response of the server.
        """

        async def perform() -> Response:
            return await self._internal_http_service.post_multipart_data(
                path=path, headers=await self._get_headers(), data=data, files=files
            )

        return await self.with_renew_token_and_retry(func=perform)

    async def patch(
        self,
        path: str,
        parameters: Optional[Dict[str, Any]] = None,
        body: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, Any]] = None,
    ) -> Response:
        """
        Patch a resource on the server.

        :param headers: Headers for httpx.AsyncClient
        :param path: Path of the resource to be patched.
        :param parameters: Parameters to pass to the server.
        :param body: JSON body of the patch request.
        :returns: Response of the server.
        """

        async def perform() -> Response:
            return await self._internal_http_service.patch(
                path=path, parameters=parameters, body=body, headers=await self._get_headers()
            )

        return await self.with_renew_token_and_retry(func=perform)

    async def delete(
        self,
        path: str,
        parameters: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, Any]] = None,
    ) -> Response:
        """
        Delete a resource on the server.

        :param headers: Headers for httpx.AsyncClient
        :param path: Path of the resource to be deleted.
        :param parameters: Parameters to pass to the server.
        :returns: Response of the server.
        """

        async def perform() -> Response:
            return await self._internal_http_service.delete(
                path=path, headers=await self._get_headers(), parameters=parameters
            )

        return await self.with_renew_token_and_retry(func=perform)

    async def _get_headers(self) -> Dict:
        if self.jwt_token == "":  # noqa: S105
            self.jwt_token = await self._authenticator_service.resolve_secret_to_access_token(
                self.auth_secret, self.auth_url
            )
        return {
            "Authorization": f"Bearer {self.jwt_token}",
            "api_version": API_VERSION,
        }

    @classmethod
    def _construct_auth_url_from_application_id(cls, api_secret: str) -> str:
        """
        Takes the first part of the api_secret (app_id:app_secret), which
        contains the Application ID, and constructs the auth url for Cognito.

        :param api_secret: API secret
        :returns: Constructed authentication URL.
        :raises AuthenticationError: If the server returned a 401 status code.
        """
        app = api_secret.split(":")
        if app[0] and isinstance(app[0], str) and app[1]:
            return f"https://{app[0]}.auth.eu-central-1.amazoncognito.com/oauth2/token"

        raise AuthenticationError("Unable to parse API URL")
