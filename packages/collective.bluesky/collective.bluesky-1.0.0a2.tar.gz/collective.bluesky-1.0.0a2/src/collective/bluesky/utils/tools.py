from collective.bluesky.app import BlueskyApp
from collective.bluesky.interfaces import IBlueskyRegistry
from zope.component import getUtility


def get_app(name: str) -> BlueskyApp:
    """Given a name, return a BlueskyApp."""
    util = getUtility(IBlueskyRegistry)
    return util.get_app(name)
