from ..models import (
    UserCreating,
    UserDeleting,
    UserDetail,
    UserReading,
    UserSummary,
    UserUpdating,
)
from .base import ModelClient


class User(
    ModelClient[
        UserCreating,
        UserReading,
        UserUpdating,
        UserDeleting,
        UserSummary,
        UserDetail,
    ]
):
    Creating = UserCreating
    Reading = UserReading
    Updating = UserUpdating
    Deleting = UserDeleting
    Summary = UserSummary
    Detail = UserDetail
