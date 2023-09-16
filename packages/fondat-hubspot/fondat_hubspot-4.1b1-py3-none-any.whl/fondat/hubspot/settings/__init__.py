"""..."""

from .users import users_resource
from fondat.resource import resource


@resource
class SettingsResource:
    """..."""

    users = users_resource


settings_resource = SettingsResource()
