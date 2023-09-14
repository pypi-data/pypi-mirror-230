from collective.bluesky import _
from collective.bluesky import logger
from collective.bluesky import utils
from collective.bluesky.app import BlueskyApp
from OFS.SimpleItem import SimpleItem
from plone.app.contentrules.actions import ActionAddForm
from plone.app.contentrules.actions import ActionEditForm
from plone.app.contentrules.browser.formhelper import ContentRuleFormWrapper
from plone.contentrules.rule.interfaces import IExecutable
from plone.contentrules.rule.interfaces import IRuleElementData
from plone.dexterity.content import DexterityContent
from plone.stringinterp.interfaces import IStringInterpolator
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from threading import Thread
from typing import Any
from zope import schema
from zope.component import adapter
from zope.i18nmessageid import Message
from zope.interface import implementer
from zope.interface import Interface


DEFAULT_TEXT = """${description}
${url}
"""

FALLBACK_TEXT = """${title}
${url}
"""


def safe_attr(element: "BlueskyAction", attr: str, default_value: str = "") -> Any:
    """Return attribute value."""
    value = getattr(element, attr, default_value)
    return value if value is not None else ""


class IBlueskyAction(Interface):
    """Definition of the configuration available for a bluesky action."""

    app = schema.Choice(
        title=_("Bluesky App"),
        description=_("App to be used"),
        vocabulary="collective.bluesky.apps",
        required=True,
    )
    language = schema.TextLine(
        title=_("Language"),
        description=_("If not set, the content language will be used."),
        default="",
        required=False,
    )
    text = schema.Text(
        title=_("Status"),
        description=_("Main text of the post."),
        default=DEFAULT_TEXT,
        required=True,
    )
    fallback_text = schema.Text(
        title=_("Status (Fallback)"),
        description=_(
            "Text to be used if the main text character count is larger than 300 characters."
        ),
        default=FALLBACK_TEXT,
        required=True,
    )


@implementer(IBlueskyAction, IRuleElementData)
class BlueskyAction(SimpleItem):
    """The implementation of the action defined before."""

    app: str = ""
    language: str = ""
    text: str = ""

    element: str = "plone.actions.Bluesky"

    @property
    def _app(self) -> BlueskyApp:
        return utils.get_app(self.app)

    @property
    def summary(self) -> Message:
        app = self._app
        handle = utils.format_handle(app.handle)
        return _(
            "Post a new status as ${handle}",
            mapping=dict(handle=handle),
        )


@implementer(IExecutable)
@adapter(Interface, IBlueskyAction, Interface)
class BlueskyActionExecutor:
    """Executor for the Bluesky Action."""

    content: DexterityContent

    def __init__(self, context, element: "BlueskyAction", event):
        """Initialize action executor."""
        self.context = context
        self.element = element
        self.event = event
        self.content = event.object
        self.app = utils.get_app(element.app)

    def _prepare_payload(self) -> dict:
        """Process the action and return a dictionary with the Bluesky message payload.

        :returns: Bluesky message payload.
        """
        content = self.content
        element = self.element
        interpolator = IStringInterpolator(content)
        main_text = interpolator(safe_attr(element, "text")).strip()
        fallback_text = interpolator(
            safe_attr(element, "fallback_text", FALLBACK_TEXT)
        ).strip()
        text = utils.select_text(main_text, fallback_text)
        if not text:
            logger.info(
                f"{content.absolute_url()} - Not posting because text and "
                "fallback_text are larger than 300 characters."
            )
            return {}
        language = safe_attr(element, "language")
        if not language:
            language = content.language if content.language else "en"
        blobs = []
        blob = utils.media_from_content(content)
        if blob:
            blobs = [blob]
        payload = {
            "text": text,
            "blobs": blobs,
            "language": language,
        }
        return payload

    def _post(self, payload: dict) -> Thread:
        """Post a status to Bluesky."""
        app = self.app
        return app.status_post(**payload)

    def __call__(self) -> bool:
        """Execute the action."""
        payload = self._prepare_payload()
        if payload:
            self._post(payload)
        return True


class BlueskyAddForm(ActionAddForm):
    """An add form for the Bluesky Action."""

    schema = IBlueskyAction
    label = _("Add Bluesky Action")
    description = _("Action to post a status using a Bluesky account.")
    form_name = _("Configure element")
    Type = BlueskyAction

    # custom template will allow us to add help text
    template = ViewPageTemplateFile("bluesky.pt")


class BlueskyAddFormView(ContentRuleFormWrapper):
    """Wrapped add form for Bluesky Action."""

    form = BlueskyAddForm


class BlueskyEditForm(ActionEditForm):
    """An edit form for the bluesky action."""

    schema = IBlueskyAction
    label = _("Edit Bluesky Action")
    description = _("Action to post a status using a Bluesky account.")
    form_name = _("Configure element")

    # custom template will allow us to add help text
    template = ViewPageTemplateFile("bluesky.pt")


class BlueskyEditFormView(ContentRuleFormWrapper):
    """Wrapped edit form for Bluesky Action."""

    form = BlueskyEditForm
