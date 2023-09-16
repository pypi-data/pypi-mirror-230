"""
Utilities to configure the aidkit python client.
"""

from typing import Optional

import altair as alt
import httpx

from aidkit_client.aidkit_api import (
    API_VERSION,
    AidkitApi,
    AuthorizingHTTPService,
    HTTPService,
)
from aidkit_client.authenticator import ExternalAuthenticatorService
from aidkit_client.exceptions import AidkitClientNotConfiguredError
from aidkit_client.plotting.plot_renderer import aidkit_altair_plot_renderer


def configure(
    base_url: str,
    auth_secret: str,
    timeout: int = 300,
) -> None:
    """
    Configure the client. Must be called before the client is used.

    This method also enables a custom renderer for Altair visualizations. In order to use another
    one, refer to https://altair-viz.github.io/user_guide/display_frontends.html#renderer-api.

    :param base_url: Base URL of the API backend.
    :param auth_secret: API secret for authentication.
    :param timeout: Timeout for httpx requests in seconds.
    """
    # we allow global setting of the configurations parameters
    global _GLOBAL_API_SERVICE  # pylint: disable=global-statement
    aidkit_api = AidkitApi(
        httpx.AsyncClient(base_url=base_url, timeout=timeout, headers={"api_version": API_VERSION})
    )
    authenticator = ExternalAuthenticatorService(httpx.AsyncClient(timeout=30))
    _GLOBAL_API_SERVICE = AuthorizingHTTPService(
        auth_secret=auth_secret,
        _internal_http_service=aidkit_api,
        _authenticator_service=authenticator,
    )

    # Initialize the renderer for the plots
    alt.renderers.register("aidkit_renderer", aidkit_altair_plot_renderer)
    alt.renderers.enable("aidkit_renderer")


_GLOBAL_API_SERVICE: Optional[HTTPService] = None


def get_api_client() -> HTTPService:
    """
    Get an API client using the current global configuration options.

    :raises AidkitClientNotConfiguredError: If the client has not been
        configured before this function is called.
    :return: Service instance using the global configuration options set via
        `aidkit_client.configure`.
    """
    if _GLOBAL_API_SERVICE is None:
        raise AidkitClientNotConfiguredError(
            """aidkit must be configured first.
        Run `aidkit_client.configure(BASE_URL, AUTH_SECRET)` before calling any other method."""
        )
    return _GLOBAL_API_SERVICE
