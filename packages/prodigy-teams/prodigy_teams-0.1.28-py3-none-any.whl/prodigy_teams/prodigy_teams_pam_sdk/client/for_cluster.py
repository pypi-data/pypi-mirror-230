from .. import ty
from ..models import (
    ActionDetail,
    ClusterJobReading,
    EmptyResponse,
    MetricsCreating,
    MetricsLogging,
    NomadAttemptUpdating,
    NomadEventBatchCreating,
    NomadEventGetIndex,
    NomadEventIndex,
    NomadJobs,
    ReportNomadJobResponse,
    TaskDetail,
)
from .base import BaseClient


class ForCluster(BaseClient):
    class Token(ty.BaseModel):
        token: str

    def read_task(self, data: ClusterJobReading, **kwargs: ty.Any) -> TaskDetail:
        res = self.request(
            "POST",
            endpoint="read-task",
            data=data,
            return_model=TaskDetail,
        )
        return ty.cast(TaskDetail, res)

    async def read_task_async(
        self, data: ClusterJobReading, **kwargs: ty.Any
    ) -> TaskDetail:
        res = await self.request_async(
            "POST",
            endpoint="read-task",
            data=data,
            return_model=TaskDetail,
        )
        return ty.cast(TaskDetail, res)

    def read_action(self, data: ClusterJobReading, **kwargs: ty.Any) -> ActionDetail:
        res = self.request(
            "POST",
            endpoint="read-action",
            data=data,
            return_model=ActionDetail,
        )
        return ty.cast(ActionDetail, res)

    async def read_action_async(
        self, data: ClusterJobReading, **kwargs: ty.Any
    ) -> ActionDetail:
        res = await self.request_async(
            "POST",
            endpoint="read-action",
            data=data,
            return_model=ActionDetail,
        )
        return ty.cast(ActionDetail, res)

    def report_nomad_event(
        self, data: NomadEventBatchCreating, **kwargs: ty.Any
    ) -> None:
        self.request(
            "POST",
            endpoint="report-nomad-event",
            data=data,
        )
        return None

    async def report_nomad_event_async(
        self, data: NomadEventBatchCreating, **kwargs: ty.Any
    ) -> None:
        await self.request_async(
            "POST",
            endpoint="report-nomad-event",
            data=data,
        )
        return None

    def update_attempt(
        self, data: NomadAttemptUpdating, **kwargs: ty.Any
    ) -> EmptyResponse:
        res = self.request(
            "POST",
            endpoint="update-attempt",
            data=data,
            return_model=EmptyResponse,
        )
        return ty.cast(EmptyResponse, res)

    async def update_attempt_async(
        self, data: NomadAttemptUpdating, **kwargs: ty.Any
    ) -> EmptyResponse:
        res = await self.request_async(
            "POST",
            endpoint="update-attempt",
            data=data,
            return_model=EmptyResponse,
        )
        return ty.cast(EmptyResponse, res)

    def report_nomad_jobs(
        self, data: ty.Union[NomadJobs, dict], **kwargs: ty.Any
    ) -> ReportNomadJobResponse:
        res = self.request(
            "POST",
            endpoint="report-nomad-jobs",
            data=data,
        )
        return ty.cast(ReportNomadJobResponse, res)

    async def report_nomad_jobs_async(
        self, data: ty.Union[NomadJobs, dict], **kwargs: ty.Any
    ) -> ReportNomadJobResponse:
        res = await self.request_async(
            "POST",
            endpoint="report-nomad-jobs",
            data=data,
            return_model=ReportNomadJobResponse,
        )
        return ty.cast(ReportNomadJobResponse, res)

    def get_nomad_event_index(self, data: NomadEventGetIndex) -> NomadEventIndex:
        res = self.request(
            "POST",
            endpoint="get-nomad-event-index",
            data=data,
            return_model=NomadEventIndex,
        )
        return ty.cast(NomadEventIndex, res)

    async def get_nomad_event_index_async(
        self, data: NomadEventGetIndex
    ) -> NomadEventIndex:
        res = await self.request_async(
            "POST",
            endpoint="get-nomad-event-index",
            data=data,
            return_model=NomadEventIndex,
        )
        return ty.cast(NomadEventIndex, res)

    def init_metrics(self, data: MetricsCreating) -> None:
        res = self.request("POST", endpoint="init-metrics", data=data)
        return ty.cast(None, res)

    async def init_metrics_async(self, data: MetricsCreating) -> None:
        res = await self.request_async("POST", endpoint="log-metrics", data=data)
        return ty.cast(None, res)

    def log_metrics(self, data: MetricsLogging) -> None:
        res = self.request("POST", endpoint="log-metrics", data=data)
        return ty.cast(None, res)

    async def log_metrics_async(self, data: MetricsLogging) -> None:
        res = await self.request_async("POST", endpoint="log-metrics", data=data)
        return ty.cast(None, res)
