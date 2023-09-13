from ..models import (
    ActionCreating,
    ActionDeleting,
    ActionDetail,
    ActionReading,
    ActionSummary,
    ActionUpdating,
)
from .base import ModelClient


class Action(
    ModelClient[
        ActionCreating,
        ActionReading,
        ActionUpdating,
        ActionDeleting,
        ActionSummary,
        ActionDetail,
    ]
):
    Creating = ActionCreating
    Reading = ActionReading
    Updating = ActionUpdating
    Deleting = ActionDeleting
    Summary = ActionSummary
    Detail = ActionDetail
