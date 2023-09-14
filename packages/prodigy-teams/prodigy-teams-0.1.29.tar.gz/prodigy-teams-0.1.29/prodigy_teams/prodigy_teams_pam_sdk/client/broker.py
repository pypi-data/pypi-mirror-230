from .. import ty
from ..models import (
    BrokerDeleting,
    BrokerDetail,
    BrokerReading,
    BrokerRegistering,
    BrokerRegistrationCreating,
    BrokerRegistrationSummary,
    BrokerSummary,
    BrokerUpdating,
)
from .base import ModelClient


class Broker(
    ModelClient[
        BrokerRegistering,
        BrokerReading,
        BrokerUpdating,
        BrokerDeleting,
        BrokerSummary,
        BrokerDetail,
    ]
):
    Creating = BrokerRegistering
    Reading = BrokerReading
    Updating = BrokerUpdating
    Deleting = BrokerDeleting
    Summary = BrokerSummary
    Detail = BrokerDetail

    class Token(ty.BaseModel):
        token: str

    def create(
        self, data: ty.Optional[BrokerRegistrationCreating] = None, **kwargs: ty.Any
    ) -> BrokerRegistrationSummary:
        data = data if data else BrokerRegistrationCreating(**kwargs)
        res = self.request(
            "POST",
            endpoint="create",
            data=data,
            return_model=BrokerRegistrationSummary,
        )
        return ty.cast(BrokerRegistrationSummary, res)

    async def create_async(
        self, data: ty.Optional[BrokerRegistrationCreating] = None, **kwargs: ty.Any
    ) -> BrokerRegistrationSummary:
        data = data if data else BrokerRegistrationCreating(**kwargs)
        res = await self.request_async(
            "POST",
            endpoint="create",
            data=data,
            return_model=BrokerRegistrationSummary,
        )
        return ty.cast(BrokerRegistrationSummary, res)

    def register(
        self, data: ty.Optional[BrokerRegistering] = None, **kwargs: ty.Any
    ) -> BrokerDetail:
        data = data if data else BrokerRegistering(**kwargs)
        res = self.request(
            "POST",
            endpoint="register",
            data=data,
            return_model=BrokerDetail,
        )
        return ty.cast(BrokerDetail, res)

    async def register_async(
        self, data: ty.Optional[BrokerRegistering] = None, **kwargs: ty.Any
    ) -> BrokerDetail:
        data = data if data else BrokerRegistering(**kwargs)
        res = await self.request_async(
            "POST",
            endpoint="register",
            data=data,
            return_model=BrokerDetail,
        )
        return ty.cast(BrokerDetail, res)
