"""Python module for accessing HomeLINK Device."""

import logging

from .alert import Alert
from .utils import ApiComponent

_LOGGER = logging.getLogger(__name__)


class Device(ApiComponent):
    """Device is the instantiation of a HomeLINK Device"""

    def __init__(self, device, parent=None, **kwargs):
        """Initialize the property."""
        super().__init__(
            parent,
            **kwargs,
        )

        self.serialnumber = device.get("serialNumber", None)
        self.model = device.get("model", None)
        self.modeltype = device.get("modelType", None)
        self.location = device.get("location", None)
        self.locationnickname = device.get("locationNickname", None)
        self.manufacturer = device.get("manufacturer", None)
        self.installationdate = device.get("installationDate", None)
        self.installedby = device.get("installedBy", None)
        self.replacedate = device.get("replaceDate", None)
        self.createdat = device.get("createdAt", None)
        self.updatedat = device.get("updatedAt", None)
        self.metadata = self.Metadata(device["metadata"])
        self.status = self.Status(device["status"])
        self._rel = self.Rel(device["_rel"])
        # _convert_dict_to_class(self, device)

    class Metadata:
        """Metadata class for device."""

        def __init__(self, metadata):
            """Initialise _Rel."""
            self.signalstrength = metadata.get("signalStrength", None)
            self.lastseendate = metadata.get("lastSeenDate", None)
            self.connectivitytype = metadata.get("connectivityType", None)

    class Status:
        """Status class for device."""

        def __init__(self, status):
            """Initialise _Rel."""
            self.operationalstatus = status.get("operationalStatus", None)
            self.lasttesteddate = status.get("lastTestedDate", None)
            self.datacollectionstatus = status.get("dataCollectionStatus", None)

    class Rel:
        """Relative URLs for device."""

        def __init__(self, _rel):
            """Initialise _Rel."""
            self.self = _rel.get("_self", None)
            self.property = _rel.get("property", None)
            self.alerts = _rel.get("alerts", None)

    async def get_alerts(self):
        """Get alerts for the Device."""
        response = await self.api.async_request("GET", self._rel.alerts)

        return [Alert(result, parent=self) for result in response.get("results", [])]
