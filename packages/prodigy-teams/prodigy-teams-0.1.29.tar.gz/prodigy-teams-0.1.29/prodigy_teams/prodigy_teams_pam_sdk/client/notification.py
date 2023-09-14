from ..models import (
    NotificationCreating,
    NotificationDeleting,
    NotificationDetail,
    NotificationReading,
    NotificationSummary,
    NotificationUpdating,
)
from .base import ModelClient


class Notification(
    ModelClient[
        NotificationCreating,
        NotificationReading,
        NotificationUpdating,
        NotificationDeleting,
        NotificationSummary,
        NotificationDetail,
    ]
):
    Creating = NotificationCreating
    Reading = NotificationReading
    Updating = NotificationUpdating
    Deleting = NotificationDeleting
    Summary = NotificationSummary
    Detail = NotificationDetail
