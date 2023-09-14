from ..models import (
    OrgCreating,
    OrgDeleting,
    OrgDetail,
    OrgReading,
    OrgSummary,
    OrgUpdating,
)
from .base import ModelClient


class Org(
    ModelClient[
        OrgCreating, OrgReading, OrgUpdating, OrgDeleting, OrgSummary, OrgDetail
    ]
):
    Creating = OrgCreating
    Reading = OrgReading
    Updating = OrgUpdating
    Deleting = OrgDeleting
    Summary = OrgSummary
    Detail = OrgDetail
