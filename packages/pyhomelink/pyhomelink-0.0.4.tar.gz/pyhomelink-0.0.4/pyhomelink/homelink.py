"""Python module for accessing HomeLINK."""

import logging

from .alert import Alert

# from .alert import Alert
from .const import (
    ENDPOINT_GET_ALERT,
    ENDPOINT_GET_DEVICE,
    ENDPOINT_GET_DEVICES,
    ENDPOINT_GET_LOOKUP,
    ENDPOINT_GET_LOOKUPS,
    ENDPOINT_GET_PROPERTIES,
    ENDPOINT_GET_PROPERTY,
)
from .device import Device
from .lookup import Lookup
from .property import Property
from .utils import ApiComponent

_LOGGER = logging.getLogger(__name__)


class HomeLINK(ApiComponent):
    """Landlord is the instantiation of the HomeLINK Landlord."""

    _endpoints = {
        ENDPOINT_GET_ALERT: "alert/{alertid}",
        ENDPOINT_GET_DEVICE: "device/{serialnumber}",
        ENDPOINT_GET_DEVICES: "device",
        ENDPOINT_GET_LOOKUP: "lookup/{lookuptype}/{id}",
        ENDPOINT_GET_LOOKUPS: "lookup/{lookuptype}",
        ENDPOINT_GET_PROPERTIES: "property",
        ENDPOINT_GET_PROPERTY: "property/{propertyreference}",
    }

    def __init__(self, **kwargs):
        """Initialize the landlord."""
        super().__init__(
            None,
            **kwargs,
        )
        self._access_token = None

    @property
    def access_token(self):
        """Return the access token."""
        return self._access_token

    async def auth(self, clientid, clientsecret):
        """Authorise to the api."""

        auth = await self.api.async_do_auth(clientid, clientsecret)
        if auth:
            self._access_token = auth
        return auth

    async def get_properties(self):
        """Get properties for the Landlord."""
        response = await self.api.async_request(
            "GET", self._endpoints.get(ENDPOINT_GET_PROPERTIES)
        )
        return [Property(result, parent=self) for result in response.get("results", [])]

    async def get_property(self, propertyreference):
        """Get a specific property by reference."""
        response = await self.api.async_request(
            "GET",
            self._endpoints.get(ENDPOINT_GET_PROPERTY).format(
                propertyreference=propertyreference
            ),
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

    async def add_property_tags(self, propertyreference, tags):
        """Add tags to a given property."""
        hl_property = await self.get_property(propertyreference)
        await hl_property.add_tags(tags)
        return hl_property.tags

    async def delete_property_tags(self, propertyreference, tags):
        """Delete tagsfrom a given property."""
        hl_property = await self.get_property(propertyreference)
        await hl_property.delete_tags(tags)
        return hl_property.tags

    async def get_devices(self):
        """Get devices for the Landlord."""
        response = await self.api.async_request(
            "GET", self._endpoints.get(ENDPOINT_GET_DEVICES)
        )
        return [Device(result, parent=self) for result in response.get("results", [])]

    async def get_device(self, serialnumber):
        """Get a specific device by serial number."""
        response = await self.api.async_request(
            "GET",
            self._endpoints.get(ENDPOINT_GET_DEVICE).format(serialnumber=serialnumber),
        )
        return Device(response, parent=self)

    async def get_device_alerts(self, serialnumber):
        """Get alerts specific device by serial number."""
        device = await self.get_device(serialnumber)
        return await device.get_alerts()

    async def get_alert(self, alertid):
        """Get a specific property by reference."""
        response = await self.api.async_request(
            "GET", self._endpoints.get(ENDPOINT_GET_ALERT).format(alertid=alertid)
        )
        return Alert(response, parent=self)

    async def get_lookups(self, lookuptype):
        """Get a lookup by lookuptype."""
        response = await self.api.async_request(
            "GET",
            self._endpoints.get(ENDPOINT_GET_LOOKUPS).format(lookuptype=lookuptype),
        )
        return [Lookup(result, parent=self) for result in response]

    async def get_lookup(self, lookuptype, lookupid):
        """Get a lookup by lookuptype and id."""
        response = await self.api.async_request(
            "GET",
            self._endpoints.get(ENDPOINT_GET_LOOKUP).format(
                lookuptype=lookuptype, id=lookupid
            ),
        )
        return Lookup(response, parent=self)
