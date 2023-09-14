from base64 import b64decode
from collections import defaultdict
from collective.bluesky import DEFAULT_HOST
from collective.bluesky import DEFAULT_PROTOCOL
from collective.bluesky.testing import INTEGRATION_TESTING
from DateTime import DateTime
from plone import api
from plone.app.multilingual.interfaces import ITranslationManager
from plone.namedfile import NamedBlobImage
from pytest_plone import fixtures_factory
from typing import List
from zope.component.hooks import setSite

import pytest


pytest_plugins = ["pytest_plone"]

globals().update(fixtures_factory(((INTEGRATION_TESTING, "integration"),)))

APPS = [
    {
        "handle": "demo",
        "app_password": "jutbgrhNDS1EvUvpoHD0ox4a7obSCT9_IpliStv799M",
    },
    {
        "host": "sandbox.bsky.social",
        "handle": "foo",
        "app_password": "jutbgrhNDS1EvUvpoHD0ox4a7obSCT9_IpliStv799M",
    },
]


@pytest.fixture
def mock_settings_bluesky_apps(mocker):
    mocker.patch("collective.bluesky.settings.get_bluesky_apps", return_value=APPS)


@pytest.fixture
def bsky_base_url():
    return f"{DEFAULT_PROTOCOL}://{DEFAULT_HOST}/xrpc"


@pytest.fixture(autouse=True)
def mock_requests(requests_mock, bsky_base_url):
    # Authentication
    requests_mock.register_uri(
        "POST",
        f"{bsky_base_url}/com.atproto.server.createSession",
        json={"did": "did:plc:u5cwb2mwiv2bfq53cjufe6yn", "accessJwt": "foo"},
        status_code=200,
    )
    # Upload Blob
    requests_mock.register_uri(
        "POST",
        f"{bsky_base_url}/com.atproto.repo.uploadBlob",
        json={
            "blob": {
                "$type": "blob",
                "ref": {
                    "$link": "bafkreibabalobzn6cd366ukcsjycp4yymjymgfxcv6xczmlgpemzkz3cfa"
                },
                "mimeType": "image/png",
                "size": 760898,
            }
        },
        status_code=200,
    )
    # Send post
    requests_mock.register_uri(
        "POST",
        f"{bsky_base_url}/com.atproto.repo.createRecord",
        json={
            "uri": "at://did:plc:u5cwb2mwiv2bfq53cjufe6yn/app.bsky.feed.post/3k4duaz5vfs2b",
            "cid": "bafyreibjifzpqj6o6wcq3hejh7y4z4z2vmiklkvykc57tw3pcbx3kxifpm",
        },
        status_code=200,
    )
    # Find user
    requests_mock.register_uri(
        "GET",
        f"{bsky_base_url}/com.atproto.identity.resolveHandle",
        json={"did": "did:plc:u5cwb2mwiv2bfq53cjufe6yn"},
        status_code=200,
    )


@pytest.fixture
def contents() -> List:
    """Content to be created."""
    future_effective_date = DateTime() + 2  # Two days in the future
    past_effective_date = DateTime() - 2  # Two days in the past
    return [
        {
            "_container": "",
            "type": "Image",
            "id": "an-image",
            "title": "A Random Image",
            "description": "With some details",
            "language": "de",
            "subject": ["Image", "Plone"],
            "_image": b"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAA1JREFUGFdjCDO+/R8ABKsCZD++CcMAAAAASUVORK5CYII=",  # noQA
        },
        {
            "_container": "",
            "type": "Document",
            "id": "future",
            "title": "Future",
            "description": "A document in the future",
            "effective_date": future_effective_date,
            "subject": ["Future", "Bluesky"],
        },
        {
            "_container": "",
            "type": "Document",
            "id": "past",
            "title": "Past",
            "description": "A document in the past",
            "effective_date": past_effective_date,
            "subject": ["Past", "Bluesky"],
        },
        {
            "_container": "",
            "type": "Document",
            "id": "document_preview",
            "title": "Illustrated document",
            "description": "A document with a preview image",
            "effective_date": past_effective_date,
            "subject": ["Preview", "Bluesky"],
            "preview_caption_link": "An image",
            "_preview_image_link": "/an-image",
        },
        {
            "_container": "",
            "type": "News Item",
            "id": "mynews",
            "title": "A News Item",
            "description": "A News Item about Bluesky",
            "subject": ["News", "Bluesky"],
            "_image": b"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAA1JREFUGFdjCDO+/R8ABKsCZD++CcMAAAAASUVORK5CYII=",  # noQA
        },
    ]


@pytest.fixture
def create_contents(contents):
    """Helper fixture to create initial content."""

    def func(portal) -> dict:
        ids = defaultdict(list)
        for item in contents:
            container_path = item["_container"]
            container = portal.unrestrictedTraverse(container_path)
            payload = {"container": container, "language": "en"}
            if "_image" in item:
                payload["image"] = NamedBlobImage(b64decode(item["_image"]))
            for key, value in item.items():
                if key.startswith("_"):
                    continue
                payload[key] = value
            content = api.content.create(**payload)
            content.language = payload["language"]
            # Relation via preview_image_link
            if "_preview_image_link" in item:
                target = api.content.get(item["_preview_image_link"])
                api.relation.create(content, target, "preview_image_link")
            # Set translation
            if "_translation_of" in item:
                source = portal.unrestrictedTraverse(item["_translation_of"])
                ITranslationManager(source).register_translation(
                    content.language, content
                )
            # Transition items
            if "_transitions" in item:
                transitions = item["_transitions"]
                for transition in transitions:
                    api.content.transition(content, transition=transition)
            content.reindexObject()
            ids[container_path].append(content.getId())
        return ids

    return func


@pytest.fixture()
def update_behaviors(get_fti):
    def update_behaviors(
        type_name: str, add: List[str] = None, remove: List[str] = None
    ):
        """Add a behavior to a content type."""
        from plone.dexterity.schema import invalidate_cache

        fti = get_fti(type_name)
        current = list(fti.behaviors)
        behaviors = [beh for beh in current if beh not in remove] + add
        fti.behaviors = tuple(behaviors)
        invalidate_cache(fti)
        return fti.behaviors

    return update_behaviors


@pytest.fixture
def app(integration, mock_settings_bluesky_apps):
    from collective.bluesky import logger
    from collective.bluesky.startup import register_apps

    register_apps(logger)
    return integration["app"]


@pytest.fixture()
def portal(app, create_contents, update_behaviors):
    """Plone portal with additional content."""
    portal = app["plone"]
    setSite(portal)
    with api.env.adopt_roles(["Manager"]):
        update_behaviors(
            type_name="Document",
            remove=["volto.preview_image"],
            add=["volto.preview_image_link"],
        )
        content_ids = create_contents(portal)

    yield portal
    with api.env.adopt_roles(["Manager"]):
        containers = sorted([path for path in content_ids.keys()], reverse=True)
        for container_path in containers:
            container = portal.unrestrictedTraverse(container_path)
            container.manage_delObjects(content_ids[container_path])


@pytest.fixture
def post_payload():
    def post_payload(**kwargs):
        payload = {
            "text": "Just a post, from myself",
            "blobs": [],
            "language": "en",
        }
        # Override default values
        if kwargs:
            payload.update(kwargs)
        return payload

    return post_payload


@pytest.fixture
def wait_for():
    def func(thread):
        if not thread:
            return
        thread.join()

    return func
