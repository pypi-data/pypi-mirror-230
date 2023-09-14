from ..models import (
    PackageCreating,
    PackageDeleting,
    PackageDetail,
    PackageListingLatest,
    PackageReading,
    PackageReadingLatest,
    PackageSummary,
    PackageUpdating,
)
from .base import VersionedModelClient


class Package(
    VersionedModelClient[
        PackageCreating,
        PackageReading,
        PackageUpdating,
        PackageDeleting,
        PackageSummary,
        PackageDetail,
        PackageReadingLatest,
        PackageListingLatest,
    ]
):
    Creating = PackageCreating
    Reading = PackageReading
    Updating = PackageUpdating
    Deleting = PackageDeleting
    Summary = PackageSummary
    Detail = PackageDetail
    ReadingLatest = PackageReadingLatest
    ListingLatest = PackageListingLatest
