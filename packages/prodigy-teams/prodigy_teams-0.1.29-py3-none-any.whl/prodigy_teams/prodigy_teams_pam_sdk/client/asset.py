from ..models import (
    AssetCreating,
    AssetDeleting,
    AssetDetail,
    AssetListingLatest,
    AssetReading,
    AssetReadingLatest,
    AssetSummary,
    AssetUpdating,
)
from .base import VersionedModelClient


class Asset(
    VersionedModelClient[
        AssetCreating,
        AssetReading,
        AssetUpdating,
        AssetDeleting,
        AssetSummary,
        AssetDetail,
        AssetReadingLatest,
        AssetListingLatest,
    ]
):
    Creating = AssetCreating
    Reading = AssetReading
    Updating = AssetUpdating
    Deleting = AssetDeleting
    Summary = AssetSummary
    Detail = AssetDetail
    ReadingLatest = AssetReadingLatest
    ListingLatest = AssetListingLatest
