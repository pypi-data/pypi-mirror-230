from ..models import (
    SecretCreating,
    SecretDeleting,
    SecretDetail,
    SecretReading,
    SecretSummary,
    SecretUpdating,
)
from .base import ModelClient


class Secret(
    ModelClient[
        SecretCreating,
        SecretReading,
        SecretUpdating,
        SecretDeleting,
        SecretSummary,
        SecretDetail,
    ]
):
    Creating = SecretCreating
    Reading = SecretReading
    Updating = SecretUpdating
    Deleting = SecretDeleting
    Summary = SecretSummary
    Detail = SecretDetail
