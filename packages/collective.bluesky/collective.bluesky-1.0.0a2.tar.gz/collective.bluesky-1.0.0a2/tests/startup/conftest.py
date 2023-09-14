import pytest


APPS = [
    # Missing app_password attribute
    {
        "host": "bsky.social",
        "handle": "foo",
    },
    # Missing handle attribute
    {
        "host": "bsky.social",
        "app_password": "123453565",
    },
    # Good entry even without a host
    {
        "handle": "foo",
        "app_password": "123453565",
    },
    # Good entry
    {
        "host": "sandbox.bsky.social",
        "handle": "foo",
        "app_password": "123453565",
    },
]


@pytest.fixture
def mock_settings_bluesky_apps(mocker):
    mocker.patch("collective.bluesky.settings.get_bluesky_apps", return_value=APPS)
