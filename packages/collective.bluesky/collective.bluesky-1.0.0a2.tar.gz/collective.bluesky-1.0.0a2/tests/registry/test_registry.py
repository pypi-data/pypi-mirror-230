from collective.bluesky.interfaces import IBlueskyRegistry
from collective.bluesky.registry import BlueskyRegistry
from zope.component import getUtility

import pytest


class TestRegistry:
    @pytest.fixture(autouse=True)
    def _init(self, app):
        self.zope_app = app

    def test_registry_discovery(self):
        registry = getUtility(IBlueskyRegistry)
        assert isinstance(registry, BlueskyRegistry)

    def test_registry_get_apps(self):
        registry = getUtility(IBlueskyRegistry)
        apps = registry.get_apps()
        assert len(apps) == 2

    def test_registry_get_app(self):
        registry = getUtility(IBlueskyRegistry)
        name = "demo-bsky.social"
        app = registry.get_app(name=name)
        assert app.name == name
