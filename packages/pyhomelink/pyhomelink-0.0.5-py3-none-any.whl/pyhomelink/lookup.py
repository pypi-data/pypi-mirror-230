"""Python module for accessing HomeLINK."""

import logging

from .utils import ApiComponent

_LOGGER = logging.getLogger(__name__)


class Lookup(ApiComponent):
    """Lookup is the instantiation of a HomeLINK Lookup"""

    def __init__(self, lookup, parent=None, **kwargs):
        """Initialize the property."""
        super().__init__(
            parent,
            **kwargs,
        )

        self.lookupid = lookup.get("id", None)
        self.code = lookup.get("code", None)
        self.name = lookup.get("name", None)
        self.description = lookup.get("description", None)
        self.active = lookup.get("active", None)
