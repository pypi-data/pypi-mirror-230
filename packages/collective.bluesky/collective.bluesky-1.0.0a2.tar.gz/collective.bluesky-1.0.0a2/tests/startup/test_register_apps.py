from collective.bluesky.interfaces import IBlueskyApp
from zope.component import getAllUtilitiesRegisteredFor

import pytest


class TestRegisterApps:
    @pytest.fixture(autouse=True)
    def _init(self, app):
        self.zope_app = app

    def test_register_apps_result(self):
        apps = getAllUtilitiesRegisteredFor(IBlueskyApp)
        assert len(apps) == 2
        assert apps[0].host == "bsky.social"
        assert apps[0].handle == "foo"
        assert apps[0].name == "foo-bsky.social"
        assert apps[1].host == "sandbox.bsky.social"
        assert apps[1].handle == "foo"
        assert apps[1].name == "foo-sandbox.bsky.social"
