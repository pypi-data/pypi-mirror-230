from collective.bluesky.interfaces import BlueskyBlob
from collective.bluesky.utils import content
from plone import api

import pytest


class TestUtilsContentMediaFromContent:
    @property
    def func(self):
        return content.media_from_content

    @pytest.fixture(autouse=True)
    def _init(self, portal):
        self.portal = portal

    @pytest.mark.parametrize(
        "path,expected",
        [
            ("/an-image", True),
            ("/document_preview", True),
            ("/future", False),
            ("/past", False),
            ("/mynews", True),
        ],
    )
    def test_media_from_content(self, path: str, expected: bool):
        content = api.content.get(path=path)
        result = self.func(content)
        if not expected:
            assert result is None
        else:
            assert isinstance(result, BlueskyBlob)

    @pytest.mark.parametrize(
        "path,expected",
        [
            # Description
            ("/an-image", "With some details"),
            # preview_caption_link
            ("/document_preview", "An image"),
            # No image_caption, fallback to title
            ("/mynews", "A News Item"),
        ],
    )
    def test_media_from_content_description(self, path: str, expected: str):
        content = api.content.get(path=path)
        result = self.func(content)
        assert result.caption == expected
