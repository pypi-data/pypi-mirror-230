from ..models import (
    RecipeCreating,
    RecipeDeleting,
    RecipeDetail,
    RecipeListingLatest,
    RecipeReading,
    RecipeReadingLatest,
    RecipeSummary,
    RecipeUpdating,
)
from .base import VersionedModelClient


class Recipe(
    VersionedModelClient[
        RecipeCreating,
        RecipeReading,
        RecipeUpdating,
        RecipeDeleting,
        RecipeSummary,
        RecipeDetail,
        RecipeReadingLatest,
        RecipeListingLatest,
    ]
):
    Creating = RecipeCreating
    Reading = RecipeReading
    Updating = RecipeUpdating
    Deleting = RecipeDeleting
    Summary = RecipeSummary
    Detail = RecipeDetail
    ReadingLatest = RecipeReadingLatest
    ListingLatest = RecipeListingLatest
