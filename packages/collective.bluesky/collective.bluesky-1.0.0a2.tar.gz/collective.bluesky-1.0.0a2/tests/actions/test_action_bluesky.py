from collective.bluesky.actions.bluesky import BlueskyAction
from collective.bluesky.actions.bluesky import BlueskyAddFormView
from collective.bluesky.actions.bluesky import BlueskyEditFormView
from plone.app.contentrules.rule import Rule
from plone.contentrules.engine.interfaces import IRuleStorage
from plone.contentrules.rule.interfaces import IExecutable
from plone.contentrules.rule.interfaces import IRuleAction
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.interface import implementer
from zope.interface.interfaces import IObjectEvent

import pytest


@pytest.fixture
def action_payload() -> dict:
    return {
        "app": "demo-bsky.social",
        "language": "en",
        "text": "Hello word! ${absolute_url}",
    }


@pytest.fixture
def bluesky_action(action_payload) -> BlueskyAction:
    e = BlueskyAction()
    for attr, value in action_payload.items():
        setattr(e, attr, value)
    return e


@implementer(IObjectEvent)
class DummyEvent:
    def __init__(self, object):
        self.object = object


class TestAction:
    name: str = "plone.actions.Bluesky"

    @pytest.fixture(autouse=True)
    def _init(self, portal):
        self.portal = portal
        self.image = portal["an-image"]

    def add_view(self, http_request):
        element = getUtility(IRuleAction, name=self.name)
        storage = getUtility(IRuleStorage)
        storage["foo"] = Rule()
        rule = self.portal.restrictedTraverse("++rule++foo")
        adding = getMultiAdapter((rule, http_request), name="+action")
        addview = getMultiAdapter((adding, http_request), name=element.addview)
        return addview

    def test_registered(self):
        element = getUtility(IRuleAction, name=self.name)
        assert self.name == element.addview
        assert "edit" == element.editview
        assert element.for_ is None

    def test_summary(self, bluesky_action):
        from zope.i18nmessageid.message import Message

        summary = bluesky_action.summary
        assert isinstance(summary, Message)
        assert summary == "Post a new status as ${handle}"
        assert summary.mapping == {"handle": "@demo.bsky.social"}

    def test_add_view(self, http_request, action_payload):
        addview = self.add_view(http_request)
        assert isinstance(addview, BlueskyAddFormView) is True
        addview.form_instance.update()
        output = addview.form_instance()
        assert "<h2>Substitutions</h2>" in output
        content = addview.form_instance.create(data=action_payload)
        addview.form_instance.add(content)
        rule = self.portal.restrictedTraverse("++rule++foo")
        e = rule.actions[0]
        assert isinstance(e, BlueskyAction)
        assert e.app == "demo-bsky.social"

    def test_edit_view(self, http_request):
        element = getUtility(IRuleAction, name=self.name)
        e = BlueskyAction()
        editview = getMultiAdapter((e, http_request), name=element.editview)
        assert isinstance(editview, BlueskyEditFormView)

    @pytest.mark.parametrize(
        "key,expected",
        [
            ("text", "Hello word! http://nohost/plone/an-image"),
        ],
    )
    def test_payload_interpolation(self, bluesky_action, key: str, expected: str):
        ex = getMultiAdapter(
            (self.portal, bluesky_action, DummyEvent(self.image)), IExecutable
        )
        payload = ex._prepare_payload()
        assert payload[key] == expected

    def test_language_from_content(self, bluesky_action):
        bluesky_action.language = ""
        ex = getMultiAdapter(
            (self.portal, bluesky_action, DummyEvent(self.image)), IExecutable
        )
        payload = ex._prepare_payload()
        assert payload["language"] == self.image.language

    @pytest.mark.vcr(match_on=["path"])
    def test_execute(self, bluesky_action, wait_for):
        ex = getMultiAdapter(
            (self.portal, bluesky_action, DummyEvent(self.image)), IExecutable
        )
        payload = ex._prepare_payload()
        wait_for(ex._post(payload))

    @pytest.mark.vcr(match_on=["path"])
    def test_call(self, bluesky_action):
        ex = getMultiAdapter(
            (self.portal, bluesky_action, DummyEvent(self.image)), IExecutable
        )
        assert ex() is True
