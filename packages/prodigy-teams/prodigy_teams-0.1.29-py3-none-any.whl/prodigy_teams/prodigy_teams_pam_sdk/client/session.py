from typing import cast

from ..models import (
    SessionCreating,
    SessionDeleting,
    SessionDetail,
    SessionReading,
    SessionSummary,
    SessionTokenReturning,
    SessionUpdating,
)
from .base import ModelClient


class Session(
    ModelClient[
        SessionCreating,
        SessionReading,
        SessionUpdating,
        SessionDeleting,
        SessionSummary,
        SessionDetail,
    ]
):
    Creating = SessionCreating
    Reading = SessionReading
    Updating = SessionUpdating
    Deleting = SessionDeleting
    Summary = SessionSummary
    Detail = SessionDetail

    def token(self, data: SessionCreating) -> SessionTokenReturning:
        res = self.request(
            "POST",
            endpoint="token",
            data=data,
            return_model=SessionTokenReturning,
        )
        return cast(SessionTokenReturning, res)

    async def token_async(self, data: SessionCreating) -> SessionTokenReturning:
        res = await self.request_async(
            "POST",
            endpoint="token",
            data=data,
            return_model=SessionTokenReturning,
        )
        return cast(SessionTokenReturning, res)
