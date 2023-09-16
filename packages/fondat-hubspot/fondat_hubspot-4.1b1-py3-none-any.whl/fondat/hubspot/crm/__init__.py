"""..."""

from .exports import exports_resource
from .objects import objects_resource
from .owners import owners_resource
from .pipelines import pipelines_resource
from .properties import properties_resource
from .schemas import schemas_resource
from fondat.resource import resource


@resource
class CRMResource:
    """..."""

    exports = exports_resource
    objects = objects_resource
    pipelines = pipelines_resource
    properties = properties_resource
    owners = owners_resource
    schemas = schemas_resource


crm_resource = CRMResource()
