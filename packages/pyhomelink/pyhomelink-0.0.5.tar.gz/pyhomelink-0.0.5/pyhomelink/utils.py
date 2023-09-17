"""Core utilities for HomeLINK service."""

from .api import API


class ApiComponent:
    """Base of all components."""

    def __init__(self, parent, **kwargs):
        self.api = parent.api if parent else API(**kwargs)
