from logging import Logger


def register_apps(logger: Logger):
    """Register Bluesky apps as utilities."""
    from collective.bluesky.app import BlueskyApp
    from collective.bluesky.interfaces import BlueskyAppInfo
    from collective.bluesky.interfaces import IBlueskyApp
    from collective.bluesky.settings import get_bluesky_apps
    from zope.component import getGlobalSiteManager

    apps_info = []
    for payload in get_bluesky_apps():
        try:
            app = BlueskyAppInfo(**payload)
        except TypeError as exc:
            logger.warning(f"Wrong format for AppInfo {exc.args}")
        else:
            apps_info.append(app)
    for info in apps_info:
        app = BlueskyApp(
            host=info.host,
            handle=info.handle,
            app_password=info.app_password,
            protocol=info.protocol,
        )
        getGlobalSiteManager().registerUtility(app, IBlueskyApp, name=app.name)
