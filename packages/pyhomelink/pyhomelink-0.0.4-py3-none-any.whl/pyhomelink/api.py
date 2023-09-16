"""Various utilities in support of HomeLINK."""
import logging

import aiohttp

from .const import AUTHURL, BASE_URL, HTTP_OK

_LOGGER = logging.getLogger(__name__)


class API:
    """API access to the HomeLINK service."""

    def __init__(self, **kwargs):
        """Initialize the api."""

        self._clientid = None
        self._clientsecret = None

        self.session = kwargs.get("session") or aiohttp.ClientSession()

        if access_token := kwargs.get("access_token", None):
            self._headers = self._build_headers(access_token)
        else:
            self._headers = None

    async def async_request(self, method, endpoint, data=None):
        """Get data from HomeLINK service."""
        if not self._headers:
            _LOGGER.error("Authentication required")
            return

        url = self._build_url(endpoint)
        return await self._async_request(method, url, data)

    async def async_do_auth(self, clientid, clientsecret):
        """Do authentication."""
        self._clientid = clientid
        self._clientsecret = clientsecret

        url = AUTHURL.format(self._clientid, self._clientsecret)
        try:
            response = await self._async_request("GET", url, None)
        except aiohttp.client_exceptions.ClientResponseError as err:
            if err.status == 401:
                return False
            raise

        access_token = response.get("accessToken")
        self._headers = self._build_headers(access_token)
        return access_token

    async def _async_request(self, method, url, data):
        http_method = {
            "DELETE": self.session.delete,
            "GET": self.session.get,
            "PATCH": self.session.patch,
            "POST": self.session.post,
            "PUT": self.session.put,
        }.get(method)
        try:
            async with http_method(
                url,
                headers=self._headers,
                json=data,
                raise_for_status=True,
                timeout=10,
            ) as response:
                if response.status != HTTP_OK:
                    _LOGGER.warning(
                        "Retrieval error, status %s, for url %s", response.status, url
                    )
                    raise RuntimeError(
                        f"Retrieval error, status {response.status}, for url {url}"
                    )

                return await response.json(content_type=None)
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
