from ..models import (
    BrokerPathCreating,
    BrokerPathDeleting,
    BrokerPathDetail,
    BrokerPathReading,
    BrokerPathSummary,
    BrokerPathUpdating,
)
from .base import ModelClient


class BrokerPath(
    ModelClient[
        BrokerPathCreating,
        BrokerPathReading,
        BrokerPathUpdating,
        BrokerPathDeleting,
        BrokerPathSummary,
        BrokerPathDetail,
    ]
):
    Creating = BrokerPathCreating
    Reading = BrokerPathReading
    Updating = BrokerPathUpdating
    Deleting = BrokerPathDeleting
    Summary = BrokerPathSummary
    Detail = BrokerPathDetail
