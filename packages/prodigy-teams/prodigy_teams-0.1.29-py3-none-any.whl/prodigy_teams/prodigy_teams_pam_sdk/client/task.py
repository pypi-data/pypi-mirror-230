from ..models import (
    TaskCreating,
    TaskDeleting,
    TaskDetail,
    TaskReading,
    TaskSummary,
    TaskUpdating,
)
from .base import ModelClient


class Task(
    ModelClient[
        TaskCreating,
        TaskReading,
        TaskUpdating,
        TaskDeleting,
        TaskSummary,
        TaskDetail,
    ]
):
    Creating = TaskCreating
    Reading = TaskReading
    Updating = TaskUpdating
    Deleting = TaskDeleting
    Summary = TaskSummary
    Detail = TaskDetail
