from collective.bluesky.app import BlueskyApp
from collective.bluesky.interfaces import IBlueskyApp
from collective.bluesky.utils import media_from_content
from plone import api
from zope.component import getAllUtilitiesRegisteredFor
from zope.component import getUtility

import pytest


DEFAULT_APP = "demo-bsky.social"


class TestAppDiscovery:
    @pytest.fixture(autouse=True)
    def _init(self, app):
        self.zope_app = app

    def test_all_apps(self):
        all_apps = getAllUtilitiesRegisteredFor(IBlueskyApp)
        assert len(all_apps) == 2

    @pytest.mark.parametrize(
        "name,host,handle",
        [
            ("demo-bsky.social", "bsky.social", "demo"),
            ("foo-sandbox.bsky.social", "sandbox.bsky.social", "foo"),
        ],
    )
    def test_app_is_registered(self, name: str, host: str, handle: str):
        app = getUtility(IBlueskyApp, name=name)
        assert isinstance(app, BlueskyApp)
        assert app.name == name
        assert app.host == host
        assert app.handle == handle


class TestAppMethods:
    app: BlueskyApp

    @pytest.fixture(autouse=True)
    def _init(self, portal):
        self.portal = portal
        self.app = getUtility(IBlueskyApp, name=DEFAULT_APP)


class TestAppStatusPost(TestAppMethods):
    @pytest.mark.vcr()
    def test_post(self, post_payload):
        payload = post_payload()
        response = self.app._status_post(**payload)
        assert isinstance(response, dict)
        assert "uri" in response
        assert "cid" in response

    @pytest.mark.vcr()
    def test_post_language(self, post_payload):
        payload = post_payload(language="pt")
        response = self.app._status_post(**payload)
        assert "uri" in response
        assert "cid" in response

    @pytest.mark.vcr(match_on=["path"])
    def test_post_with_media(self, post_payload):
        content = api.content.get("/an-image")
        blobs = [media_from_content(content)]
        payload = post_payload(blobs=blobs)
        response = self.app._status_post(**payload)
        assert "uri" in response
        assert "cid" in response
