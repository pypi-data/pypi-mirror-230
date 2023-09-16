"""HubSpot authentication module."""

import aiohttp

from fondat.error import UnauthorizedError
from urllib.parse import urlencode


_AUTH_ENDPOINT = "https://app.hubspot.com/oauth/authorize"
_TOKEN_ENDPOINT = "https://api.hubapi.com/oauth/v1/token"


def generate_authorization_url(
    *,
    endpoint: str = _AUTH_ENDPOINT,
    client_id: str,
    scopes: list[str],
    redirect_uri: str,
    optional_scopes: list[str] | None = None,
    state: str | None = None,
) -> str:
    """
    Generate a redirect URL to request an authorization code.

    Parameters:
    • endpoint: authorization URL endpoint
    • client_id: application client identifier
    • scopes: scopes that the application is requesting
    • redirect_uri: URL that user will be redirected to after authorization
    • optional_scopes: the scopes that are optional to the application
    • state: unique string that can be used to maintain the user's state
    """

    params = {
        "client_id": client_id,
        "scope": " ".join(scopes),
        "redirect_uri": redirect_uri,
        "optional_scope": " ".join(optional_scopes) if optional_scopes else None,
        "state": state,
    }

    return (
        endpoint.rstrip("/")
        + "?"
        + urlencode({k: v for k, v in params.items() if v is not None})
    )


async def request_refresh_token(
    *,
    session: aiohttp.ClientSession,
    endpoint: str = _TOKEN_ENDPOINT,
    client_id: str,
    client_secret: str,
    redirect_uri: str,
    code: str,
) -> str:
    """
    Request an refresh token using an authorization code.

    Parameters:
    • session: client session to use for HTTP requests
    • endpoint: token endpoint
    • client_id: application's client identifier
    • client_secret: application's client secret
    • redirect_uri: URL that user was redirected to after authorization
    • code: authorization code received from authorization server
    """

    async with await session.post(
        url=endpoint.rstrip("/"),
        data={
            "grant_type": "authorization_code",
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri,
            "code": code,
        },
    ) as response:
        json = await response.json()
        if response.status == 200:
            return json["refresh_token"]
        raise UnauthorizedError(json["error"])


def access_token_authenticator(*, access_token: str):
    """
    Return a coroutine that returns a fixed access token. Access token authentication is
    used in HubSpot for private applications.

    Parameters:
    • access_token: access token to return
    """

    async def authenticate(session: aiohttp.ClientSession) -> str:
        return access_token

    return authenticate


def refresh_token_authenticator(
    *,
    endpoint: str = _TOKEN_ENDPOINT,
    client_id: str,
    client_secret: str,
    redirect_uri: str,
    refresh_token: str,
):
    """
    Return a coroutine that returns an access token acquired via refresh token flow. Refresh
    token authentication is used in HubSpot for connected applications.

    Parameters:
    • session: client session to use for HTTP requests
    • endpoint: token endpoint
    • client_id: application's client identifier
    • client_secret: application's client secret
    • redirect_uri: URL that user was redirected to after authorization
    • refresh_token: refresh token received when user authorized application
    """

    async def authenticate(session: aiohttp.ClientSession) -> str:
        async with await session.post(
            url=endpoint.rstrip("/"),
            data={
                "grant_type": "refresh_token",
                "client_id": client_id,
                "client_secret": client_secret,
                "redirect_uri": redirect_uri,
                "refresh_token": refresh_token,
            },
        ) as response:
            json = await response.json()
            if response.status == 200:
                return json["access_token"]
            raise UnauthorizedError(json["error"])

    return authenticate
