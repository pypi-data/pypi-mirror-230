"""..."""

from datetime import datetime
from fondat.data import datacls
from fondat.hubspot.client import get_client
from fondat.resource import operation, resource
from typing import Any, Literal, TypedDict


@datacls
class PipelineStage:
    id: str
    label: str
    displayOrder: int
    metadata: dict[str, Any]
    createdAt: datetime
    updatedAt: datetime
    archivedAt: datetime | None
    archived: bool
    writePermissions: str


@datacls
class Pipeline:
    id: str
    label: str
    displayOrder: int
    stages: list[PipelineStage]
    createdAt: datetime
    updatedAt: datetime
    archivedAt: datetime | None
    archived: bool


@resource
class PipelineStageResource:
    """..."""

    def __init__(self, objectType: str, pipelineId: str, stageId: str):
        self.objectType = objectType
        self.pipelineId = pipelineId
        self.stageId = stageId

    @operation
    async def get(self) -> PipelineStage:
        return await get_client().typed_request(
            method="GET",
            path=f"/crm/v3/pipelines/{self.objectType}/{self.pipelineId}/stages/{self.stageId}",
            response_type=PipelineStage,
        )


@resource
class PipelineStagesResource:
    """..."""

    def __init__(self, objectType: str, pipelineId: str):
        self.objectType = objectType
        self.pipelineId = pipelineId

    @operation
    async def get(self) -> list[PipelineStage]:
        """..."""
        response = await get_client().typed_request(
            method="GET",
            path=f"/crm/v3/pipelines/{self.objectType}/{self.pipelineId}/stages",
            response_type=TypedDict("TD", {"results": list[PipelineStage]}),
        )
        return response["results"]

    def __getitem__(self, stageId: str) -> PipelineStageResource:
        return PipelineStageResource(self.objectType, self.pipelineId, stageId)


@resource
class PipelineResource:
    """..."""

    def __init__(self, objectType: str, pipelineId: str):
        self.objectType = objectType
        self.pipelineId = pipelineId

    @operation
    async def get(self) -> Pipeline:
        """..."""
        return await get_client().typed_request(
            method="GET",
            path="/crm/v3/pipelines/{self.objectType}/{self.pipelineId}",
            response_type=Pipeline,
        )

    @property
    def stages(self) -> PipelineStagesResource:
        return PipelineStagesResource(self.objectType, self.pipelineId)


@resource
class PipelineObjectResource:
    """..."""

    def __init__(self, objectType: str):
        self.objectType = objectType

    @operation
    async def get(self) -> list[Pipeline]:
        """..."""
        response = await get_client().typed_request(
            method="GET",
            path=f"/crm/v3/pipelines/{self.objectType}",
            response_type=TypedDict("TD", {"results": list[Pipeline]}),
        )
        return response["results"]

    def __getitem__(self, pipelineId) -> PipelineResource:
        return PipelineResource(self.objectType, pipelineId)


@resource
class PipelinesResource:
    """..."""

    def __getitem__(self, objectType: str):
        return PipelineObjectResource(objectType)


pipelines_resource = PipelinesResource()
