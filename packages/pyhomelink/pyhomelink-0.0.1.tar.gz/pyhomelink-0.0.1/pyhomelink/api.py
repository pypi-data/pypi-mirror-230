"""Various utilities in support of HomeLINK."""
import asyncio
import json
import logging

import aiohttp

from .const import AUTHURL, BASE_URL, HTTP_OK

_LOGGER = logging.getLogger(__name__)


class API:
    """API access to the HomeLINK service."""

    def __init__(self, **kwargs):
        """Initialize the api."""
        if not kwargs.get("websession", None):
            _LOGGER.error("Async session must be supplied")
            return

        if (
            not kwargs.get("access_token", None)
            and not kwargs.get("clientid", None)
            and not kwargs.get("clientsecret", None)
        ):
            _LOGGER.error(
                "Either access key, or client_id and client_secret must be supplied"
            )
            return

        self._websession = kwargs.get("websession")
        if access_token := kwargs.get("access_token", None):
            self._headers = self._build_headers(access_token)
        else:
            self._headers = None
            self._clientid = kwargs.get("clientid")
            self._clientsecret = kwargs.get("clientsecret")

    async def async_get_data(self, endpoint):
        """Get data from HomeLINK service."""
        if not self._headers:
            await self._async_do_auth()
        url = self._build_url(endpoint)
        try:
            async with getattr(self._websession, "get")(
                url, headers=self._headers
            ) as response:
                if response.status != HTTP_OK:
                    _LOGGER.warning(
                        "Retrieval error, status %s, for url %s", response.status, url
                    )
                    raise RuntimeError(
                        f"Retrieval error, status {response.status}, for url {url}"
                    )

                responsedata = await response.text()
                return json.loads(responsedata)
        except asyncio.TimeoutError as err:
            raise RuntimeError(
                "Connection to HomeLINK service failed with timeout"
            ) from err

        except aiohttp.client_exceptions.ClientConnectorError as err:
            raise RuntimeError(
                "Connection to HomeLINK service failed with Connection Error"
            ) from err

    def _build_url(self, endpoint):
        """Returns a url for a given endpoint ."""
        return f"{BASE_URL}{endpoint}"

    def _build_headers(self, access_token):
        return {
            "accept": "application/json",
            "Authorization": f"Bearer {access_token}",
        }

    async def _async_do_auth(self):
        """ "Do authentication."""
        url = AUTHURL.format(self._clientid, self._clientsecret)
        try:
            async with getattr(self._websession, "get")(url, headers=None) as response:
                if response.status != HTTP_OK:
                    raise RuntimeError(
                        f"Connection to HomeLINK service failed with error {response.status}"
                    )

                responsedata = await response.text()
                access_token = json.loads(responsedata).get("accessToken")
                self._headers = self._build_headers(access_token)
        except asyncio.TimeoutError as err:
            raise RuntimeError(
                "Connection to HomeLINK service failed with timeout"
            ) from err

        except aiohttp.client_exceptions.ClientConnectorError as err:
            raise RuntimeError(
                "Connection to HomeLINK service failed with Connection Error"
            ) from err
