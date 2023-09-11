"""..."""

from datetime import datetime
from fondat.codec import JSONCodec
from fondat.data import datacls
from fondat.hubspot.client import get_client
from fondat.pagination import Cursor, Page
from fondat.resource import operation, resource
from fondat.validation import MaxValue, MinValue
from typing import Annotated


@datacls
class OwnerTeam:
    id: str
    name: str
    primary: bool


@datacls
class Owner:
    id: str
    email: str
    firstName: str
    lastName: str
    userId: int | None
    createdAt: datetime
    updatedAt: datetime
    archived: bool
    teams: list[OwnerTeam] | None


@resource
class OwnerResource:
    """..."""

    def __init__(self, ownerId: str):
        self.ownerId = ownerId

    @operation
    async def get(self) -> Owner:
        return await get_client().typed_request(
            method="GET",
            path=f"/crm/v3/owners/{self.ownerId}",
            response_type=Owner,
        )


@resource
class OwnersResource:
    """..."""

    @operation
    async def get(
        self,
        limit: Annotated[int, MinValue(1), MaxValue(100)] = 100,
        cursor: Cursor = None,
    ) -> Page[Owner]:
        return await get_client().paged_request(
            method="GET",
            path=f"/crm/v3/owners",
            item_type=Owner,
            limit=limit,
            cursor=cursor,
        )

    def __getitem__(self, ownerId: str) -> OwnerResource:
        return OwnerResource(ownerId)


owners_resource = OwnersResource()
