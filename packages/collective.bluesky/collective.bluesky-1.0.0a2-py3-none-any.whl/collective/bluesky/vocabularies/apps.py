from collective.bluesky.interfaces import IBlueskyRegistry
from collective.bluesky.utils import format_handle
from zope.component import getUtility
from zope.interface import provider
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


@provider(IVocabularyFactory)
def bluesky_apps(_):
    """List registered Bluesky apps."""
    registry = getUtility(IBlueskyRegistry)
    apps = registry.get_apps()
    terms = []
    for app in apps:
        title = format_handle(app.handle)
        terms.append(SimpleTerm(value=app.name, token=app.name, title=title))

    return SimpleVocabulary(terms)
