"""A client used to communicate with the Validio API."""
from http import HTTPStatus
from pathlib import Path

import httpx

import validio_sdk.metadata
from validio_sdk.config import Config, ValidioConfig
from validio_sdk.graphql_client.client import Client

HOME_DIR = str(Path.home())


class UnauthorizedError(Exception):
    """Exception thrown when unauthorized request is made."""

    def __init__(self):
        """Construct the exception."""
        super().__init__(
            "🛑 Unauthorized!\nEnsure you're using working credentials.\nIf you're"
            " using the validio config file, make you have working credentials and add"
            " them by running 'validio config'"
        )


class ValidioAPIClient(Client):
    """An API client used to communicate with the Validio API."""

    def __init__(
        self,
        headers: dict[str, str] | None = None,
        validio_config: ValidioConfig | None = None,
    ):
        """
        Create a new API client.

        :param headers: Custom headers to apply to each request
        :param http_client: HTTP client to use for API calls
        :param validio_config: Config for the client to initialize from

        :returns: A `ValidioAPIClient` object
        """
        if validio_config is None:
            validio_config = Config().read()

        base_url = validio_config.endpoint
        graphql_endpoint = f"{base_url}/graphql"
        base_headers = {"user-agent": f"validio-sdk@{validio_sdk.metadata.version()}"}
        http_client = httpx.AsyncClient(
            headers=base_headers,
            auth=_add_api_token_auth_header(validio_config),
            timeout=30,
            event_hooks={"response": [_handle_unauthorized]},
        )

        super().__init__(graphql_endpoint, headers, http_client)


async def _handle_unauthorized(response: httpx.Response):
    if response.status_code == HTTPStatus.UNAUTHORIZED:
        raise UnauthorizedError


def _add_api_token_auth_header(validio_config: ValidioConfig):
    """
    Add the API token to the authorization header.

    The format is: Authorization: <access_key>:<access_secret>
    """

    def inner(request: httpx.Request) -> httpx.Request:
        request.headers["Authorization"] = (
            f"{validio_config.access_key}:{validio_config._access_secret}"
        )
        return request

    return inner
