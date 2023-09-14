from collective.bluesky.utils import username

import pytest


class TestUtilsUsername:
    @pytest.mark.parametrize(
        "handle,expected",
        [
            ("user", "@user.bsky.social"),
            ("user.com", "@user.com"),
            ("ericof.com", "@ericof.com"),
            ("plone.org", "@plone.org"),
        ],
    )
    def test_format_handle(self, handle: str, expected: str):
        func = username.format_handle
        assert func(handle) == expected

    @pytest.mark.parametrize(
        "handle,expected",
        [
            ("user.bsky.social", True),
            ("user.com", True),
            ("xn--ls8h.test", True),
            ("jo@hn.test", False),
            ("💩.test", False),
            ("name.org", True),
            ("user", False),
            ("org", False),
            ("laptop.local", False),
            ("laptop.arpa", False),
            ("2gzyxa5ihm7nsggfxnu52rck2vv4rvmdlkiu3zzui5du4xyclen53wid.onion", False),
            ("", False),
            ("foo.localhost", False),
            ("foo.local", False),
            ("foo.onion", False),
            ("foo.internal", False),
        ],
    )
    def test_validate_handle(self, handle: str, expected: bool):
        func = username.validate_handle
        assert func(handle) is expected
