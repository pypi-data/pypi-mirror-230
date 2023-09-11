"""HubSpot CRM export module."""

import asyncio

from collections.abc import AsyncIterator, Iterable
from contextlib import asynccontextmanager, suppress
from datetime import datetime
from fondat.codec import Codec, DecodeError, StringCodec
from fondat.csv import CSVReader, TypedDictCodec
from fondat.data import datacls
from fondat.file import FileResource
from fondat.http import AsBody
from fondat.hubspot.client import HTTPResponseStream, get_client
from fondat.hubspot.crm.model import Filter, Property
from fondat.hubspot.crm.properties import properties_resource
from fondat.resource import mutation, query, resource
from fondat.stream import IOBaseStream
from fondat.validation import validate_arguments
from pathlib import Path
from tempfile import NamedTemporaryFile
from time import time
from typing import Annotated, Any, Literal, TypedDict
from zipfile import ZipFile


Format = Literal["XLSX", "CSV", "XLS"]


@datacls
class Sort:
    propertyName: str
    order: Literal["ASC", "DES"]


@datacls
class _ExportRequest:
    """..."""

    @datacls
    class PublicCRMSearchRequest:
        filters: list[Filter]
        sorts: list[Sort]
        query: str

    exportType: Literal["LIST", "VIEW"]
    objectType: str
    objectProperties: list[str]
    format: Format
    exportName: str
    associatedObjectType: str | None = None
    language: str | None = None
    listId: str | None = None
    publicCrmSearchRequest: PublicCRMSearchRequest | None = None


@datacls
class ExportResponse:
    id: str
    links: dict[str, Any]


@datacls
class ExportTaskError:
    """..."""

    @datacls
    class Category:
        name: str
        httpStatus: str

    @datacls
    class Error:
        message: str
        in_: str
        code: str
        subCategory: str
        context: dict[str, Any]

    status: str
    id: str
    category: Category
    subCategory: dict[str, Any]
    message: str
    errors: list[Error]
    context: dict[str, Any]
    links: dict[str, Any]


@datacls
class ExportTaskStatus:
    """..."""

    status: Literal["COMPLETE", "PENDING", "PROCESSING", "CANCELED"]
    result: str | None
    numErrors: int | None
    errors: list[ExportTaskError] | None
    requestedAt: datetime | None
    startedAt: datetime
    completedAt: datetime
    links: dict[str, Any] | None


@resource
class ExportTaskResource:
    """..."""

    def __init__(self, taskId: str):
        self.taskId = taskId

    @query
    async def status(self) -> ExportTaskStatus:
        """Retrieve asynchronous export task status."""
        return await get_client().typed_request(
            method="GET",
            path=f"/crm/v3/exports/export/async/tasks/{self.taskId}/status",
            response_type=ExportTaskStatus,
        )


@resource
class ExportsResource:
    """..."""

    @mutation
    async def export_list(
        self,
        *,
        objectType: str,
        objectProperties: list[str],
        format: Format,
        exportName: str,
        associatedObjectType: str | None = None,
        language: str | None = None,
        listId: str,
    ) -> ExportResponse:
        "Create an asynchronous export list task."
        return await get_client().typed_request(
            method="POST",
            path=f"/crm/v3/exports/export/async",
            request_body=_ExportRequest(
                exportType="LIST",
                objectType=objectType,
                objectProperties=objectProperties,
                format=format,
                exportName=exportName,
                associatedObjectType=associatedObjectype,
                language=language,
                listId=listId,
            ),
            response_type=ExportResponse,
        )

    @mutation
    async def export_view(
        self,
        *,
        objectType: str,
        objectProperties: list[str],
        format: Format,
        exportName: str,
        associatedObjectType: str | None = None,
        language: str | None = None,
        filters: list[Filter],
        sorts: list[Sort],
        query: str,
    ) -> ExportResponse:
        "Create an asynchronous export view task."
        return await get_client().typed_request(
            method="POST",
            path=f"/crm/v3/exports/export/async",
            request_body=_ExportRequest(
                exportType="VIEW",
                objectType=objectType,
                objectProperties=objectProperties,
                format=format,
                exportName=exportName,
                associatedObjectType=associatedObjectType,
                language=language,
                publicCrmSearchRequest=_ExportRequest.PublicCRMSearchRequest(
                    filters=filters,
                    sorts=sorts,
                    query=query,
                ),
            ),
            response_type=ExportResponse,
        )

    def __getitem__(self, taskId: str) -> ExportTaskResource:
        return ExportTaskResource(taskId)


exports_resource = ExportsResource()


class _SingleEnumCodec(Codec[str, str]):
    """..."""

    field_types = {"booleancheckbox", "number", "radio", "select"}

    def __init__(self, property: Property):
        if property.type != "enumeration":
            raise ValueError("expecting enumeration property")
        if property.fieldType not in self.field_types:
            raise ValueError(f"expecting field type: {self.field_types}")
        self._l2v = {o.label: o.value for o in property.options}

    def encode(self, value: str) -> str:
        raise NotImplementedError

    def decode(self, value: str) -> str:
        try:
            return self._l2v.get(value, value)
        except KeyError:
            return value


class _MultiEnumCodec(Codec[set[str], str]):
    """..."""

    field_types = {"checkbox"}

    def __init__(self, property: Property):
        if property.type != "enumeration":
            raise ValueError("expecting enumeration property")
        if property.fieldType not in self.field_types:
            raise ValueError(f"expecting field type: {self.field_types}")
        self._l2v = {o.label: o.value for o in property.options}

    def decode(self, value: str) -> set[str]:
        result = set()
        for value in value.split(";"):
            if value := value.strip():
                result.add(self._l2v.get(value, value))
        return result


class _BestEffortCodec(Codec[str, Any]):
    """Decodes on best-effort basis, reverting to undecoded string on decode error."""

    def __init__(self, property: Property):
        self.codec = StringCodec.get(property.python_type)

    def decode(self, value: str) -> Any:
        try:
            return self.codec.decode(value)
        except DecodeError:
            return value


def _property_codec(property: Property) -> Codec[str, Any]:
    match property.type:
        case "enumeration":
            for codec in {_SingleEnumCodec, _MultiEnumCodec}:
                if property.fieldType in codec.field_types:
                    return codec(property)
        case _:
            return _BestEffortCodec(property)
    raise ValueError(f"cannot find codec for property: {property}")


def _associated_property(singular: str, plural: str) -> Property:
    return Property(
        name=f"associated{singular}ids",
        label=f"Associated {singular.title()} IDs",
        type="enumeration",
        fieldType="checkbox",
        description=f"Associated {plural}.",
        groupName="associations",
        options=[],
        displayOrder=-1,
        calculated=False,
        externalOptions=True,
        hasUniqueValue=False,
        hidden=True,
        hubspotDefined=True,
        modificationMetadata=Property.ModificationMetadata(
            archivable=False, readOnlyDefinition=True, readOnlyOptions=None, readOnlyValue=False
        ),
        formField=False,
    )


_associated_properties = {
    "companies": _associated_property("company", "companies"),
    "contacts": _associated_property("contact", "contacts"),
    "deals": _associated_property("deal", "deals"),
}


AssociatedObjectType = Literal[tuple(_associated_properties.keys())]


@asynccontextmanager
async def _delete(resource):
    yield
    with suppress(Exception):
        await resource.delete()


@validate_arguments
async def export(
    *,
    objectType: str,
    properties: list[Property],
    exportName: str,
    filters: list[Filter] | None = None,
    associatedObjectType: AssociatedObjectType | None = None,
    sorts: list[Sort] | None = None,
    query: str | None = None,
    timeout: int | None = None,
) -> AsyncIterator[dict[str, Any]]:
    """
    Perform a bulk export of objects from HubSpot, decoding properties into their associated
    Python types on a best-effort basis.

    This function uses the export endpoint in HubSpot, which is intended to produce a
    human-readable spreadsheet, not a precise machine-readable raw export of data. This results
    in some limitations:

    1. Headers contain non-unique labels instead of unique names. Some properties share the
    same label, making them ambiguous in the response. Requesting an export with ambiguously
    labeled properties will raise an error.

    2. Values may not conform with their property definitions. Examples: a) some ID
    properties are returned as names, b) some checkbox enumerations encode arbitrary lists of
    values in a single property. If a property cannot be decoded, it will be left as an
    undecoded string.

    Parameters:
    • objectType: the name or ID of the object to export
    • properties: properties to include in the export
    • exportName: name of the export
    • filters: property values to filter records by
    • associatedObjectType: name or ID of the associated object to include
    • sorts: sort order of the property values
    • query: string to search object values for
    • timeout: seconds to wait for query job to complete  [unlimited]

    This function downloads the export payload to a temporary file, as it can be a zip archive
    that requires extraction.
    """

    keys = {}

    for property in properties:
        if property.label in keys:
            raise ValueError(f"multiple properties have same label: {prop.label}")
        keys[property.label] = property.name

    export_response = await exports_resource.export_view(
        objectType=objectType,
        objectProperties=[p.name for p in properties],
        format="CSV",
        exportName=exportName,
        associatedObjectType=associatedObjectType,
        filters=filters or [],
        sorts=sorts or [],
        query=query or "",
    )

    task_resource = exports_resource[export_response.id]

    start = time()
    sleep = 1

    while True:
        task = await task_resource.status()
        match task.status:
            case "COMPLETE":
                break
            case "CANCELLED":
                raise RuntimeError("export task was cancelled")
        if timeout and time() - start >= timeout:
            raise asyncio.exceptions.TimeoutError
        await asyncio.sleep(sleep)
        sleep = min(sleep * 2, 60)

    row_codec = None

    if associatedObjectType:  # add expected association column
        aprop = _associated_properties[associatedObjectType]
        properties = properties + [aprop]
        keys[aprop.label] = aprop.name

    session = get_client().session

    async with session.request("GET", task.result) as response:
        if response.status != 200:
            raise InternalServerError(
                f"unexpected response: {response.status} {await response.text()}"
            )

        with NamedTemporaryFile(delete=False) as tmpfile:  # let it close
            tmp_path = Path(tmpfile.name)

        download = FileResource(tmp_path, writable=True)

        async with _delete(download):
            await download.put(HTTPResponseStream(response))

            match response.content_type:
                case "text/csv":
                    stream = await download.get()
                case "application/zip":
                    with ZipFile(tmp_path) as zip:
                        names = zip.namelist()
                        if len(names) > 1:
                            raise RuntimeError("zip archive has more than one member")
                        stream = IOBaseStream(zip.open(names[0]))
                case _:
                    raise RuntimeError("unexpected content type: {response.content_type}")

            async with stream:  # close after reading
                async for row in CSVReader(stream):
                    if not row_codec:  # first row is header
                        row_codec = TypedDictCodec(
                            typeddict=TypedDict("Row", {p.name: Any for p in properties}),
                            columns=row,
                            keys=keys,
                            codecs={p.label: _property_codec(p) for p in properties},
                        )
                        continue
                    yield row_codec.decode(row)
