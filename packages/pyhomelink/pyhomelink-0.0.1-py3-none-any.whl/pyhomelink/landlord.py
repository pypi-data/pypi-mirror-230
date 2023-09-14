"""Python module for accessing Landlord."""

import logging

from .alert import Alert

# from .alert import Alert
from .const import (
    ENDPOINT_GET_ALERT,
    ENDPOINT_GET_DEVICE,
    ENDPOINT_GET_DEVICES,
    ENDPOINT_GET_PROPERTIES,
    ENDPOINT_GET_PROPERTY,
)
from .device import Device
from .property import Property
from .utils import ApiComponent

_LOGGER = logging.getLogger(__name__)


class Landlord(ApiComponent):
    """Landlord is the instantiation of the HomeLINK Landlord."""

    _endpoints = {
        ENDPOINT_GET_ALERT: "alert/{alertid}",
        ENDPOINT_GET_DEVICE: "device/{serialnumber}",
        ENDPOINT_GET_DEVICES: "device",
        # ENDPOINT_GET_DEVICE_ALERTS: "device/{serialnumber}/alerts",
        ENDPOINT_GET_PROPERTIES: "property",
        ENDPOINT_GET_PROPERTY: "property/{propertyreference}",
        # ENDPOINT_GET_PROPERTY_ALERTS: "property/{propertyreference}/alerts",
        # ENDPOINT_GET_PROPERTY_DEVICES: "property/{propertyreference}/devices",
    }

    def __init__(self, **kwargs):
        """Initialize the landlord."""
        super().__init__(
            None,
            **kwargs,
        )

    async def get_properties(self):
        """Get properties for the Landlord."""
        response = await self.api.async_get_data(
            self._endpoints.get(ENDPOINT_GET_PROPERTIES)
        )

        return [Property(result, parent=self) for result in response.get("results", [])]

    async def get_property(self, propertyreference):
        """Get a specific property by reference."""
        response = await self.api.async_get_data(
            self._endpoints.get(ENDPOINT_GET_PROPERTY).format(
                propertyreference=propertyreference
            )
        )
        return Property(response, parent=self)

    async def get_property_devices(self, propertyreference):
        """Get devices for a specific property by reference."""
        hl_property = await self.get_property(propertyreference)
        return await hl_property.get_devices()

    async def get_property_alerts(self, propertyreference):
        """Get alerts for a specific property by reference."""
        hl_property = await self.get_property(propertyreference)
        return await hl_property.get_alerts()

    async def get_devices(self):
        """Get devices for the Landlord."""
        response = await self.api.async_get_data(
            self._endpoints.get(ENDPOINT_GET_DEVICES)
        )

        return [Device(result, parent=self) for result in response.get("results", [])]

    async def get_device(self, serialnumber):
        """Get a specific device by serial number."""
        response = await self.api.async_get_data(
            self._endpoints.get(ENDPOINT_GET_DEVICE).format(serialnumber=serialnumber)
        )
        return Device(response, parent=self)

    async def get_device_alerts(self, serialnumber):
        """Get alerts specific device by serial number."""
        device = await self.get_device(serialnumber)
        return await device.get_alerts()

    async def get_alert(self, alertid):
        """Get a specific property by reference."""
        response = await self.api.async_get_data(
            self._endpoints.get(ENDPOINT_GET_ALERT).format(alertid=alertid)
        )
        return Alert(response, parent=self)
