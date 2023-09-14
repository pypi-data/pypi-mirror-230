from collective.bluesky import DEFAULT_HOST
from collective.bluesky import DEFAULT_PROTOCOL
from dataclasses import dataclass
from typing import List
from zope.interface import Interface


@dataclass
class BlueskyAppInfo:
    """Bluesky App Information."""

    handle: str
    app_password: str
    protocol: str = DEFAULT_PROTOCOL
    host: str = DEFAULT_HOST


@dataclass
class BlueskyBlob:
    """Bluesky media object."""

    data: bytes
    mime_type: str
    caption: str
    size: int


class IBlueskyRegistry(Interface):
    """A singleton utility listing a."""

    def get_app(name):
        """Returns a BlueskyApp."""

    def get_apps():
        """Returns a list of registered apps."""


class IBlueskyApp(Interface):
    """A named utility for bluesky."""

    _base_url: str
    name: str
    handle: str
    app_password: str
    host: str

    def status_post(
        text: str,
        blobs: List[BlueskyBlob],
        language: str,
    ):
        """Post a status."""
