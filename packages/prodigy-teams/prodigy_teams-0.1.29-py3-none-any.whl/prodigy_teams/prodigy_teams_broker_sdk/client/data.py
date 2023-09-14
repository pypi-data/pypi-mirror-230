from .. import ty
from ..models import Dataset, DatasetCreating, PageDatasetExample
from .base import BaseClient


class Data(BaseClient):
    def all(
        self,
        session: ty.Optional[bool] = None,
        *,
        page: ty.Optional[int] = None,
        size: ty.Optional[int] = None,
    ) -> ty.Page[str]:
        res = self.request(
            "GET",
            endpoint="all",
            data={"session": session},
            page=page,
            size=size,
            return_model=ty.Page[str],
        )
        return ty.cast(ty.Page[str], res)

    async def all_async(
        self,
        session: ty.Optional[bool] = None,
        *,
        page: ty.Optional[int] = None,
        size: ty.Optional[int] = None,
    ) -> ty.Page[str]:
        res = await self.request_async(
            "GET",
            endpoint="all",
            data={"session": session},
            page=page,
            size=size,
            return_model=ty.Page[str],
        )
        return ty.cast(ty.Page[str], res)

    def create(self, body: DatasetCreating) -> Dataset:
        res = self.request("POST", endpoint="create", data=body, return_model=Dataset)
        return ty.cast(Dataset, res)

    async def create_async(self, body: DatasetCreating) -> Dataset:
        res = await self.request_async(
            "POST", endpoint="create", data=body, return_model=Dataset
        )
        return ty.cast(Dataset, res)

    def read_examples(
        self,
        datasets: list[str],
        *,
        page: ty.Optional[int] = None,
        size: ty.Optional[int] = None,
        order: ty.Optional[ty.Literal["asc", "desc"]] = "asc",
    ) -> PageDatasetExample:
        params: dict = {}
        if page is not None:
            params["page"] = page
        if size is not None:
            params["size"] = size
        if order is not None:
            params["order"] = order

        data = {"datasets": datasets}

        res = self.request(
            "POST",
            endpoint="read-examples",
            params=params,
            data=data,
            return_model=PageDatasetExample,
        )
        return ty.cast(PageDatasetExample, res)

    async def read_examples_async(
        self,
        datasets: list[str],
        *,
        page: ty.Optional[int] = None,
        size: ty.Optional[int] = None,
        order: ty.Optional[ty.Literal["asc", "desc"]] = "asc",
    ) -> PageDatasetExample:
        params: dict = {}
        if page is not None:
            params["page"] = page
        if size is not None:
            params["size"] = size
        if order is not None:
            params["order"] = order

        data = {"datasets": datasets}

        res = await self.request_async(
            "POST",
            endpoint="read-examples",
            params=params,
            data=data,
            return_model=PageDatasetExample,
        )
        return ty.cast(PageDatasetExample, res)
