from ..models import (
    DatasetCreating,
    DatasetDeleting,
    DatasetDetail,
    DatasetReading,
    DatasetSummary,
    DatasetUpdating,
)
from .base import ModelClient


class Dataset(
    ModelClient[
        DatasetCreating,
        DatasetReading,
        DatasetUpdating,
        DatasetDeleting,
        DatasetSummary,
        DatasetDetail,
    ]
):
    Creating = DatasetCreating
    Reading = DatasetReading
    Updating = DatasetUpdating
    Deleting = DatasetDeleting
    Summary = DatasetSummary
    Detail = DatasetDetail
