from ..models import (
    InvitationCreating,
    InvitationDeleting,
    InvitationDetail,
    InvitationReading,
    InvitationSummary,
    InvitationUpdating,
)
from .base import ModelClient


class Invitation(
    ModelClient[
        InvitationCreating,
        InvitationReading,
        InvitationUpdating,
        InvitationDeleting,
        InvitationSummary,
        InvitationDetail,
    ]
):
    Creating = InvitationCreating
    Reading = InvitationReading
    Updating = InvitationUpdating
    Deleting = InvitationDeleting
    Summary = InvitationSummary
    Detail = InvitationDetail
