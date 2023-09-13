from .. import ty
from ..models import (
    PersonCreating,
    PersonDeleting,
    PersonDetail,
    PersonReading,
    PersonSummary,
    PersonUpdating,
)
from .base import ModelClient


class Person(
    ModelClient[
        PersonCreating,
        PersonReading,
        PersonUpdating,
        PersonDeleting,
        PersonSummary,
        PersonDetail,
    ]
):
    Creating = PersonCreating
    Reading = PersonReading
    Updating = PersonUpdating
    Deleting = PersonDeleting
    Summary = PersonSummary
    Detail = PersonDetail

    class Authenticating(ty.BaseModel):
        """
        Data describing a Person derived from an identity token provided
        by an authentication provider such as Auth0. Used during signup and login.
        """

        email: str
        name: str
        token: str
