"""..."""

from fondat.data import datacls
from fondat.hubspot.client import get_client
from fondat.pagination import Page
from fondat.resource import operation, resource
from fondat.validation import MaxValue, MinValue
from typing import Annotated, Any, Literal, TypedDict


@datacls
class ListMetadata:
    """..."""

    processing: str
    size: int
    error: str
    lastProcessingStageChangeAt: int | None
    lastSizeChangeAt: int
    listReferencesCount: int | None
    parentFolderId: int | None


@datacls
class List:
    """..."""

    listId: int
    dynamic: bool
    name: str
    filters: list[Any]
    portalId: int
    createdAt: int
    updatedAt: int
    listType: Literal["STATIC", "DYNAMIC"]
    internalListId: int | None
    deleteable: bool | None
    metaData: ListMetadata
    authorId: int
    archived: bool
    teamIds: list[int]
    ilsFilterBranch: str
    readOnly: bool
    internal: bool
    limitExempt: bool
    parentId: int | None


Identity = TypedDict(
    "Identity", {"type": str, "value": str, "timestamp": int, "is-primary": bool}
)

IdentityProfile = TypedDict(
    "IdentityProfile",
    {
        "vid": int,
        "saved-at-timestamp": int,
        "deleted-changed-timestamp": int,
        "identities": list[Identity],
    },
)

ListContact = TypedDict(
    "ListContact",
    {
        "addedAt": int,
        "vid": int,
        "canonical-vid": int,
        "merged-vids": list[int],
        "portal-id": int,
        "is-contact": bool,
        "properties": dict[str, Any],
        "form-submissions": Any,
        "identity-profiles": Any,
        "merge-audits": Any,
    },
)


@resource
class ListContactsResource:
    """..."""

    def __init__(self, listId: int):
        self.listId = listId

    @operation
    async def get(
        self,
        properties: list[str] | None = None,
        propertyMode: Literal["value_only", "value_and_history"] = "value_only",
        formSubmissionMode: Literal["all", "none", "newest", "oldest"] = "newest",
        showListMemberships: bool = False,
        limit: Annotated[int, MinValue(1), MaxValue(100)] = 100,
        cursor: bytes | None = None,
    ) -> Page[ListContact]:
        Response = TypedDict(
            "Response",
            {"contacts": list[ListContact], "has-more": bool, "vid-offset": int | None},
        )
        response = await get_client().typed_request(
            method="GET",
            path=f"/contacts/v1/lists/{self.listId}/contacts/all",
            params=dict(
                count=limit,
                vidOffset=int(cursor.decode()) if cursor else None,
                property=StringCodec.get(list[str]).encode(properties) if properties else None,
                propertyMode=propertyMode,
                formSubmissionMode=formSubmissionMode,
                showListMemberships=showListMemberships,
            ),
            response_type=Response,
        )
        return Page(
            items=response["contacts"],
            cursor=str(response["vid-offset"]).encode() if response["has-more"] else None,
        )


@resource
class ListResource:
    """..."""

    def __init__(self, listId: int):
        self.listId = listId

    @operation
    async def get(self) -> List:
        return await get_client().typed_request(
            method="GET", path=f"/contacts/v1/lists/{self.listId}", response_type=List
        )

    @property
    def contacts(self) -> ListContactsResource:
        return ListContactsResource(self.listId)


@resource
class ListsResource:
    """..."""

    @operation
    async def get(self, limit: int | None = None, cursor: bytes | None = None) -> Page[List]:
        """..."""
        Response = TypedDict(
            "Response",
            {"lists": list[List], "offset": int | None, "has-more": bool, "total": int | None},
        )
        response = await get_client().typed_request(
            method="GET",
            path="/contacts/v1/lists",
            params=dict(
                count=limit,
                offset=int(cursor.decode()) if cursor else None,
            ),
            response_type=Response,
        )
        return Page(
            items=response["lists"],
            cursor=str(response["offset"]).encode() if response["has-more"] else None,
        )

    def __getitem__(self, listId: int) -> ListResource:
        return ListResource(listId)


lists_resource = ListsResource()
