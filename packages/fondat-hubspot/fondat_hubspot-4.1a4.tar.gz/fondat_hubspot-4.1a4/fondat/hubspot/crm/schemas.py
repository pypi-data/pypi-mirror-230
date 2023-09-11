"""..."""

from datetime import datetime
from fondat.data import datacls
from fondat.hubspot.client import get_client
from fondat.hubspot.crm.model import Property
from fondat.resource import operation, resource
from typing import TypedDict


@datacls
class Association:
    """..."""

    fromObjectTypeId: str
    toObjectTypeId: str
    name: str
    id: str
    createdAt: datetime | None
    updatedAt: datetime | None


@datacls
class Labels:
    """..."""

    singular: str
    plural: str


@datacls
class Schema:
    """..."""

    labels: Labels
    primaryDisplayProperty: str
    archived: bool
    id: str
    fullyQualifiedName: str
    createdAt: datetime
    updatedAt: datetime
    objectTypeId: str
    properties: list[Property]
    associations: list[Association]
    name: str


@resource
class SchemasResource:
    """Defines how custom objects store and represent information."""

    async def get(self) -> list[Schema]:
        """Return all custom object schemas."""
        response = await get_client().typed_request(
            method="GET",
            path=f"/crm/v3/schemas",
            response_type=TypedDict("TD", {"results": list[Schema]}),
        )
        return response["results"]


schemas_resource = SchemasResource()
