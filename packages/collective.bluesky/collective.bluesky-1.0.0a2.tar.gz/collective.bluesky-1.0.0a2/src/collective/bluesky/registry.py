from collective.bluesky.app import BlueskyApp
from collective.bluesky.interfaces import IBlueskyApp
from collective.bluesky.interfaces import IBlueskyRegistry
from typing import List
from zope.component import getAllUtilitiesRegisteredFor
from zope.component import getUtility
from zope.interface import implementer


@implementer(IBlueskyRegistry)
class BlueskyRegistry:
    """Bluesky Utility"""

    def get_app(self, name: str) -> BlueskyApp:
        """Return a named Bluesky application."""
        return getUtility(IBlueskyApp, name=name)

    def get_apps(self) -> List[BlueskyApp]:
        """Return a list of registered Bluesky applications."""
        return getAllUtilitiesRegisteredFor(IBlueskyApp)
