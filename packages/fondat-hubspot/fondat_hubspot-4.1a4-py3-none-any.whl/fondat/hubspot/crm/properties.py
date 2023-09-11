"""HubSpot CRM properties resources module."""

from datetime import date, datetime
from fondat.codec import JSONCodec
from fondat.data import datacls
from fondat.hubspot.client import get_client
from fondat.hubspot.crm.model import Property
from fondat.resource import operation, resource
from typing import Any, Literal, TypedDict


@resource
class PropertyResource:
    """..."""

    def __init__(self, objectType: str, propertyName: str):
        self.objectType = objectType
        self.propertyName = propertyName

    @operation
    async def get(self) -> Property:
        """Read property."""
        return await get_client().typed_request(
            method="GET",
            path=f"/crm/v3/properties/{self.objectType}/{self.propertyName}",
            response_type=Property,
        )


@resource
class ObjectResource:
    """..."""

    def __init__(self, objectType: str):
        self.objectType = objectType

    async def get(self) -> list[Property]:
        """Read all properties for the object."""
        response = await get_client().typed_request(
            method="GET",
            path=f"/crm/v3/properties/{self.objectType}",
            response_type=TypedDict("TD", {"results": list[Property]}),
        )
        return response["results"]

    def __getitem__(self, propertyName: str) -> PropertyResource:
        return PropertyResource(self.objectType, propertyName)


@resource
class PropertiesResource:
    """..."""

    def __getitem__(self, objectType: str) -> ObjectResource:
        return ObjectResource(objectType)


properties_resource = PropertiesResource()
