from Acquisition import aq_base
from collective.bluesky.interfaces import BlueskyBlob
from collective.bluesky.settings import IMAGE_SIZE_LIMIT
from collective.bluesky.settings import IMAGE_WIDTH
from collective.bluesky.settings import IMAGE_WIDTH_FALLBACK
from collective.bluesky.settings import POST_CHAR_LIMIT
from plone.dexterity.content import DexterityContent
from plone.scale.storage import IImageScaleStorage
from typing import Union
from zope.component import getMultiAdapter


__all__ = [
    "media_from_content",
]


IMAGE_ORDER = [
    ("opengraph_image_link", "image_caption", "relation"),
    ("opengraph_image", "image_caption", "field"),
    ("preview_image_link", "preview_caption_link", "relation"),
    ("preview_image", "preview_caption", "field"),
    ("image_link", "image_caption", "relation"),
    ("image", "image_caption", "field"),
]


def get_scale(content: DexterityContent, image_field: str) -> bytes:
    """Get scale data."""
    storage = getMultiAdapter((content, None), IImageScaleStorage)
    for width in (IMAGE_WIDTH, IMAGE_WIDTH_FALLBACK):
        scale = storage.scale(fieldname=image_field, width=width)
        data = scale["data"].data if "data" in scale else b""
        if data and len(data) < IMAGE_SIZE_LIMIT:
            return data
    return data


def media_from_content(content: DexterityContent) -> Union[BlueskyBlob, None]:
    """Parse a content item and return a BlueskyBlob object."""
    content = aq_base(content)
    for field_name, field_caption, field_type in IMAGE_ORDER:
        title = content.title
        description = content.description
        # Image does not have an attribute image_caption
        if content.portal_type == "Image":
            caption = description
        else:
            caption = getattr(content, field_caption, None)
        field = getattr(content, field_name, None)
        if not field:
            continue
        if field_type == "relation":
            content = field.to_object
            caption = caption if caption else (content.description or content.title)
            field_name = "image"
            field = getattr(content, field_name, None)
        scale = get_scale(content, field_name)
        storage = getMultiAdapter((content, None), IImageScaleStorage)
        scale = storage.scale(fieldname=field_name)
        # Only upload if scale is present
        if scale:
            caption = caption if caption else title
            return BlueskyBlob(
                data=scale,
                mime_type=field.contentType,
                caption=caption,
                size=len(scale),
            )


def select_text(text: str, fallback_text: str) -> str:
    """Based on the character limit, select which text should be used."""
    len_text = len(text)
    len_fallback_text = len(fallback_text)
    if len_text <= POST_CHAR_LIMIT:
        return text
    elif len_fallback_text <= POST_CHAR_LIMIT:
        return fallback_text
    else:
        # No text is under the POST_CHAR_LIMIT
        return ""
