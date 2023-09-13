from ..models import (
    ProjectCreating,
    ProjectDeleting,
    ProjectDetail,
    ProjectReading,
    ProjectSummary,
    ProjectUpdating,
)
from .base import ModelClient


class Project(
    ModelClient[
        ProjectCreating,
        ProjectReading,
        ProjectUpdating,
        ProjectDeleting,
        ProjectSummary,
        ProjectDetail,
    ]
):
    Creating = ProjectCreating
    Reading = ProjectReading
    Updating = ProjectUpdating
    Deleting = ProjectDeleting
    Summary = ProjectSummary
    Detail = ProjectDetail
