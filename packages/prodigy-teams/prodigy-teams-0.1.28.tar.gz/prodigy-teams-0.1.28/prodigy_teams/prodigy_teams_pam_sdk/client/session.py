from ..models import (
    SessionCreating,
    SessionDeleting,
    SessionDetail,
    SessionReading,
    SessionSummary,
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
