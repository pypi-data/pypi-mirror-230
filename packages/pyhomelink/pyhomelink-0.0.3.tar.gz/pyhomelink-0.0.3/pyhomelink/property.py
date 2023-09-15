"""Python module for accessing HomeLINK Property."""

import logging

from .alert import Alert
from .const import ENDPOINT_PROPERTY_TAGS
from .device import Device
from .utils import ApiComponent

_LOGGER = logging.getLogger(__name__)


class Property(ApiComponent):
    """Property is the instantiation of a HomeLINK Property"""

    _endpoints = {
        ENDPOINT_PROPERTY_TAGS: "{propertyurl}/tags",
    }

    def __init__(self, hl_property, parent=None, **kwargs):
        """Initialize the property."""
        super().__init__(
            parent,
            **kwargs,
        )

        self.reference = hl_property.get("reference", None)
        self.createdat = hl_property.get("createdAt", None)
        self.updatedat = hl_property.get("updatedAt", None)
        self.postcode = hl_property.get("postcode", None)
        self.latitude = hl_property.get("latitude", None)
        self.longitude = hl_property.get("longitude", None)
        self.address = hl_property.get("address", None)
        self.tags = hl_property.get("tags", None)
        self._rel = self.Rel(hl_property["_rel"])

    class Rel:
        """Relative URLs for property."""

        def __init__(self, _rel):
            """Initialise _Rel."""
            self.self = _rel.get("_self", None)
            self.devices = _rel.get("devices", None)
            self.alerts = _rel.get("alerts", None)
            self.readings = _rel.get("readings", None)
            self.insights = _rel.get("insights", None)

    async def get_devices(self):
        """Get devices for the Property."""
        response = await self.api.async_request("GET", self._rel.devices)

        return [Device(result, parent=self) for result in response.get("results", [])]

    async def get_alerts(self):
        """Get alerts for the Property."""
        response = await self.api.async_request("GET", self._rel.alerts)

        return [Alert(result, parent=self) for result in response.get("results", [])]

    async def add_tags(self, tags):
        """Add tag to the Property."""
        body = {"tagIds": tags}
        response = await self.api.async_request(
            "PUT",
            self._endpoints.get(ENDPOINT_PROPERTY_TAGS).format(
                propertyurl=self._rel.self
            ),
            body,
        )
        self.tags = response.get("tags", None)
        return self.tags

    async def delete_tags(self, tags):
        """Delete tag from the Property."""
        body = {"tagIds": tags}
        response = await self.api.async_request(
            "DELETE",
            self._endpoints.get(ENDPOINT_PROPERTY_TAGS).format(
                propertyurl=self._rel.self
            ),
            body,
        )
        self.tags = response.get("tags", None)
        return self.tags
