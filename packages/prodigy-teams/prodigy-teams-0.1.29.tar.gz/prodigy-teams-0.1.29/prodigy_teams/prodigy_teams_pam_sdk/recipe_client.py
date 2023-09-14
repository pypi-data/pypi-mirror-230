import uuid
from datetime import datetime

import pydantic

from . import ty
from .client.full_client import AccessTokenCredential, Client
from .models import MetricsCreating, MetricsLogging

SUPPORTED = [int, float, str]
MetricsValue = ty.Union[int, float, str, ty.BaseModel]


class Settings(ty.BaseSettings):
    pam_token: str = ""
    pam_host: str = ""
    job_id: ty.Optional[ty.UUID] = None
    execution_id: ty.Optional[ty.UUID] = None
    broker_id: ty.Optional[ty.UUID] = None

    def validate(self) -> bool:
        values = [
            self.pam_token,
            self.pam_host,
            self.job_id,
            self.execution_id,
            self.broker_id,
        ]
        return all(x for x in values)

    class Config:
        env_prefix = "PRODIGY_TEAMS_"


def get_pam_client(pam_host: str, pam_token: str) -> Client:
    client_base_url = pydantic.HttpUrl.build(scheme="https", host=pam_host)
    token = AccessTokenCredential(access_token=pam_token)
    return Client(client_base_url, token=token)


class Metrics:
    client: ty.Optional[Client]
    name: str
    id: ty.UUID
    type: ty.Type[MetricsValue]

    def __init__(self, name: str, metric_type: ty.Type[MetricsValue]) -> None:
        self._validate_type(metric_type)
        self.cfg = Settings()
        is_valid = self.cfg.validate()
        if is_valid:
            self.client = get_pam_client(self.cfg.pam_host, self.cfg.pam_token)
        else:
            self.client = None
        self.name = name
        self.id = uuid.uuid4()
        self.type = metric_type
        self.initialize()

    @property
    def type_schema(self) -> ty.Dict[str, ty.Any]:
        if isinstance(self.type, ty.BaseModel):
            return self.type.schema()
        return {"type": self.type.__name__}

    def initialize(self) -> None:
        if self.client is not None:
            assert self.cfg.job_id
            assert self.cfg.execution_id
            body = MetricsCreating(
                id=self.id,
                name=self.name,
                job_id=self.cfg.job_id,
                execution_id=self.cfg.execution_id,
                metrics_schema=self.type_schema,
            )
            self.client.for_cluster.init_metrics(body)
        else:  # TODO
            print("INIT METRICS", self.name, self.type_schema)

    def log(self, value: MetricsValue, final: bool = False) -> None:
        if not isinstance(value, self.type):
            raise ValueError(
                f"Can't log metric of type {type(value)}: doesn't match "
                f"specified metrics type ({self.type})"
            )
        data = value.json() if isinstance(value, ty.BaseModel) else value
        timestamp = datetime.now()
        if self.client is not None:
            body = MetricsLogging(
                timestamp=timestamp, id=self.id, value=data, final=final
            )
            self.client.for_cluster.log_metrics(body)
        else:  # TODO
            print("LOG METRICS", self.name, timestamp, data)

    def _validate_type(self, metric_type: ty.Type[MetricsValue]) -> None:
        if metric_type not in SUPPORTED and not isinstance(
            metric_type, type(ty.BaseModel)
        ):
            raise ValueError(
                f"Unsupported metrics type {metric_type}. The type can either "
                f"be one of {SUPPORTED} or a pydantic.BaseModel subclass"
            )
