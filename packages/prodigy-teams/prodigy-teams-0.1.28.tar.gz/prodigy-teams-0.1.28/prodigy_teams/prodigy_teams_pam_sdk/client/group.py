from ..models import (
    GroupAuthorizing,
    GroupCreating,
    GroupDeleting,
    GroupDetail,
    GroupPopulating,
    GroupReading,
    GroupSummary,
    GroupUpdating,
)
from .base import ModelClient


class Group(
    ModelClient[
        GroupCreating,
        GroupReading,
        GroupUpdating,
        GroupDeleting,
        GroupSummary,
        GroupDetail,
    ]
):
    Creating = GroupCreating
    Reading = GroupReading
    Updating = GroupUpdating
    Deleting = GroupDeleting
    Summary = GroupSummary
    Detail = GroupDetail
    Populating = GroupPopulating
    Authorizing = GroupAuthorizing
