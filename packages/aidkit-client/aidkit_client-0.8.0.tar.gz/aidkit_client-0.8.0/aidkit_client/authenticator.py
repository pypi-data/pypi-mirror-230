"""
Handles exchanging secret for JWT token.
"""
import asyncio
import base64
import json
from abc import ABC, abstractmethod
from typing import Optional

import httpx

from aidkit_client.exceptions import AuthenticationError


class AuthenticatorService(ABC):
    """
    Abstract Authenticator service.
    """

    @abstractmethod
    async def resolve_secret_to_access_token(self, auth_secret: str, auth_url: str) -> asyncio.Task:
        """
        Resolves secret to access token via an asyncio task. The purpose of
        this is that subsequent calls while the task is running will return the
        running task.

        :param auth_secret: API secret
        :param auth_url: Auth URL
        :returns: asyncio Task
        """

    @abstractmethod
    async def get_token(self, auth_secret: str, auth_url: str) -> str:
        """
        Resolves secret to access token.

        :param auth_secret: API secret
        :param auth_url: Auth URL
        :returns: JWT token
        """


class ExternalAuthenticatorService(AuthenticatorService):
    """
    Exchanges the Secret for a JWT.
    """

    client: httpx.AsyncClient
    get_future_value: Optional[asyncio.Task]

    def __init__(self, client: httpx.AsyncClient) -> None:
        """
        Create a new instance with a client.

        :param client: HTTPX Async Client to use
        """
        self.client = client
        self.get_future_value = None

    async def resolve_secret_to_access_token(self, auth_secret: str, auth_url: str) -> asyncio.Task:
        """
        Resolves secret to access token via an asyncio task. The purpose of
        this is that subsequent calls while the task is running will return the
        running task.

        :param auth_secret: API secret
        :param auth_url: Auth URL
        :returns: asyncio Task
        """
        if self.get_future_value is None:
            self.get_future_value = asyncio.create_task(self.get_token(auth_secret, auth_url))
            result = await self.get_future_value
            self.get_future_value = None
            return result
        return await self.get_future_value

    async def get_token(self, auth_secret: str, auth_url: str) -> str:
        """
        Resolves secret to access token.

        :param auth_secret: API secret
        :param auth_url: Auth URL
        :raises AuthenticationError: auth error
        :returns: JWT token
        """
        encoded_secret = base64.b64encode(auth_secret.encode()).decode("utf-8")
        if not auth_secret:
            raise AuthenticationError("API secret is empty")
        if not auth_url:
            raise AuthenticationError("Auth URL is empty")

        try:
            client = self.client
            response = await client.post(
                url=auth_url,
                data={"grant_type": "client_credentials"},
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                    "authorization": f"Basic {encoded_secret}",
                },
            )
        except httpx.ConnectError as exc:
            raise AuthenticationError("Authentication URL is not connectable") from exc
        except httpx.TimeoutException as exc:
            raise AuthenticationError("Timed out while contacting authentication service") from exc

        try:
            json_response = json.loads(response.text)
        except json.decoder.JSONDecodeError as exc:
            raise AuthenticationError(
                "Failed to decode output from authentication service"
            ) from exc

        if (
            response.status_code == 400
            and json_response["error"]
            and json_response["error"] == "invalid_client"
        ):
            raise AuthenticationError("The API secret is not valid")

        if json_response["access_token"]:
            return json_response["access_token"]

        raise AuthenticationError("JWT token missing from authentication service output")
