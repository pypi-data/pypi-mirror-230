from prettyconf import config


IMAGE_WIDTH = config("BLUESKY_IMAGE_WIDTH", cast=int, default=1920)
IMAGE_WIDTH_FALLBACK = config("BLUESKY_IMAGE_WIDTH_FALLBACK", cast=int, default=600)
IMAGE_SIZE_LIMIT = config("BLUESKY_IMAGE_SIZE_LIMIT", cast=int, default=1000000)
POST_CHAR_LIMIT = config("BLUESKY_POST_CHAR_LIMIT", cast=int, default=300)


def get_bluesky_apps():
    return config("BLUESKY_APPS", cast=config.json, default="[]")
