"""Python module for accessing HomeLINK Alert."""

import logging

from .utils import ApiComponent

_LOGGER = logging.getLogger(__name__)


class Alert(ApiComponent):
    """Alert is the instantiation of a HomeLINK Alert"""

    def __init__(self, alert, parent=None, **kwargs):
        """Initialize the property."""
        super().__init__(
            parent,
            **kwargs,
        )

        self.alertid = alert.get("id", None)
        self.serialnumber = alert.get("serialNumber", None)
        self.description = alert.get("description", None)
        self.eventtype = alert.get("eventType", None)
        self.propertyreference = alert.get("propertyReference", None)
        self.model = alert.get("model", None)
        self.modeltype = alert.get("modelType", None)
        self.location = alert.get("location", None)
        self.locationnickname = alert.get("locationNickname", None)
        self.createdat = alert.get("createdAt", None)
        self.updatedat = alert.get("updatedAt", None)
        self.insightid = alert.get("insightId", None)
        self.severity = alert.get("severity", None)
        self.category = alert.get("category", None)
        self.type = alert.get("type", None)
        self.status = alert.get("status", None)
        self._rel = self.Rel(alert["_rel"])

    class Rel:
        """Relative URLs for Alert."""

        def __init__(self, _rel):
            """Initialise _Rel."""
            self.property = _rel.get("property", None)
            self.self = _rel.get("_self", None)
            self.device = _rel.get("device", None)
