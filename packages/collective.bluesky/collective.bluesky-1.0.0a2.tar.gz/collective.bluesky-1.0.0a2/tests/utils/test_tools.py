from collective.bluesky.utils import tools

import pytest


class TestUtilsTools:
    @pytest.mark.parametrize(
        "host,handle",
        [
            ("sandbox.bsky.social", "foo"),
            ("bsky.social", "demo"),
        ],
    )
    def test_get_app(self, app, host: str, handle: str):
        func = tools.get_app
        name = f"{handle}-{host}"
        app = func(name)
        assert app.host == host
        assert app.handle == handle
