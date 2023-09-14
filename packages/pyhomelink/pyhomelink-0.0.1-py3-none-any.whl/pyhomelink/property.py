"""Python module for accessing Landlord."""

import logging

from .alert import Alert
from .device import Device
from .utils import ApiComponent

_LOGGER = logging.getLogger(__name__)


class Property(ApiComponent):
    """Property is the instantiation of a HomeLINK Property"""

    def __init__(self, hl_property, parent=None, **kwargs):
        """Initialize the property."""
        super().__init__(
            parent,
            **kwargs,
        )

        self.reference = hl_property.get("reference", None)
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
            self._self = _rel.get("_self", None)
            self.devices = _rel.get("devices", None)
            self.alerts = _rel.get("alerts", None)
            self.readings = _rel.get("readings", None)
            self.insights = _rel.get("insights", None)

    async def get_devices(self):
        """Get devices for the Property."""
        response = await self.api.async_get_data(self._rel.devices)

        return [Device(result, parent=self) for result in response.get("results", [])]

    async def get_alerts(self):
        """Get alerts for the Property."""
        response = await self.api.async_get_data(self._rel.alerts)

        return [Alert(result, parent=self) for result in response.get("results", [])]
