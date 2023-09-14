"""Init and utils."""
from collective.bluesky import startup
from zope.i18nmessageid import MessageFactory

import logging


PACKAGE_NAME = "collective.bluesky"


DEFAULT_HOST = "bsky.social"
DEFAULT_PROTOCOL = "https"

# regex based on: https://atproto.com/specs/handle#handle-identifier-syntax
HANDLE_VALIDATOR = rb"(([a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)"
HANDLE_IDENTIFIER = rb"[$|\W](@([a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)"


_ = MessageFactory(PACKAGE_NAME)

logger = logging.getLogger(PACKAGE_NAME)


startup.register_apps(logger)
