"""..."""

from contextlib import suppress
from datetime import date, datetime
from fondat.codec import Codec, DecodeError, JSONCodec
from fondat.data import datacls
from fondat.hubspot.client import get_client
from fondat.hubspot.crm.model import Filter, Property
from fondat.pagination import Cursor, Page
from fondat.resource import operation, query, resource
from fondat.validation import MaxValue, MinValue
from typing import Annotated, Any


@datacls
class UpdatedProperty:
    value: Any
    timestamp: datetime
    sourceType: str | None
    sourceId: str | None


@datacls
class Object:
    id: str
    properties: dict[str, Any]
    propertiesWithHistory: dict[str, list[UpdatedProperty]] | None
    createdAt: datetime
    updatedAt: datetime
    archived: bool
    archivedAt: bool | None
    associations: dict[str, Any] | None


class _MultiValueCodec(Codec[set[str] | None, str | None]):
    """..."""

    def __init__(self):
        super().__init__(python_type=str | None)

    def encode(self, value: set[str]) -> str:
        raise NotImplementedError

    def decode(self, value: str | None) -> set[str] | None:
        if value is None:
            return None
        result = set()
        for value in value.split(";"):
            if value := value.strip():
                result.add(value)
        return result


_multi_value_codec = _MultiValueCodec()


def _codecs(properties: list[Property] | None) -> dict[str, Codec[Any, Any]]:
    result = {}
    for property in properties or {}:
        match property.type:
            case "bool":
                codec = JSONCodec.get(bool | None)
            case "date":
                codec = JSONCodec.get(date | None)
            case "datetime":
                codec = JSONCodec.get(datetime | None)
            case "string" | "phone_number":
                codec = JSONCodec.get(str | None)
            case "number":
                codec = JSONCodec.get(int | float | None)
            case "enumeration":
                match property.fieldType:
                    case "checkbox":
                        codec = _multi_value_codec
                    case _:
                        codec = JSONCodec.get(str | None)
            case _:
                raise ValueError(f"unexpected property.type: {property.type}")
        result[property.name] = codec
    return result


def _decode_object(object: Object, codecs: dict[str, Codec[Any, Any]]) -> None:
    """Decode properties and propertiesWithHistory values on best-effort basis."""
    for key in object.properties or ():
        if codec := codecs.get(key):
            with suppress(DecodeError):
                object.properties[key] = codec.decode(object.properties[key])
    for key in object.propertiesWithHistory or ():
        if codec := codecs.get(key):
            for update in object.propertiesWithHistory[key]:
                with suppress(DecodeError):
                    update.value = codec.decode(update.value)


@resource
class ObjectResource:
    """..."""

    def __init__(self, objectType: str, objectId: str):
        self.objectType = objectType
        self.objectId = objectId

    @operation
    async def get(
        self,
        properties: list[Property] | None = None,
        propertiesWithHistory: list[Property] | None = None,
        associations: set[str] | None = None,
        archived: bool = False,
    ) -> Object:
        item = await get_client().typed_request(
            method="GET",
            path=f"/crm/v3/objects/{self.objectType}/{self.objectId}",
            response_type=Object,
            params=dict(
                properties=[p.name for p in properties or ()] or None,
                propertiesWithHistory=[p.name for p in propertiesWithHistory or ()] or None,
                associations=associations,
                archived=archived,
            ),
        )
        _decode_object(item, _codecs(properties) | _codecs(propertiesWithHistory))
        return item


@resource
class ObjectTypeResource:
    """..."""

    def __init__(self, objectType: str):
        self.objectType = objectType

    def __getitem__(self, objectId: str) -> ObjectResource:
        return ObjectResource(self.objectType, objectId)

    @operation
    async def get(
        self,
        properties: list[Property],
        propertiesWithHistory: list[Property] | None = None,
        associations: set[str] | None = None,
        archived: bool = False,
        limit: Annotated[int, MinValue(1), MaxValue(100)] = 100,
        cursor: Cursor = None,
    ) -> Page[Object]:
        """Return a paginated list of objects."""
        page = await get_client().paged_request(
            method="GET",
            path=f"/crm/v3/objects/{self.objectType}",
            item_type=Object,
            limit=limit,
            cursor=cursor,
            params=dict(
                properties=[p.name for p in properties or ()] or None,
                propertiesWithHistory=[p.name for p in propertiesWithHistory or ()] or None,
                associations=associations,
                archived=archived,
            ),
        )
        codecs = _codecs(properties) | _codecs(propertiesWithHistory)
        for item in page.items:
            _decode_object(item, codecs)
        return page


@resource
class ObjectsResource:
    """..."""

    def __getitem__(self, objectType: str) -> ObjectTypeResource:
        return ObjectTypeResource(objectType)


objects_resource = ObjectsResource()
