"""..."""

from .lists import lists_resource
from fondat.resource import resource


@resource
class ContactsResource:
    """..."""

    lists = lists_resource


contacts_resource = ContactsResource()
