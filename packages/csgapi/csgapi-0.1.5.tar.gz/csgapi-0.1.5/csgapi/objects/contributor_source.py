from typing import cast

from csgapi.types import ForeignKeyManager
from ..base import RESTManager, RESTObject, RequiredOptional
from ..mixin import APIObject

__all__ = [
    "ContributorSource",
    "ContributorSourceManager",
]


class ContributorSource(APIObject, RESTObject):
    pass


# NOTE: even tho Delete Mixin is integrated, since has_processor is a look up table,
# our API does not support DELETE for it
class ContributorSourceManager(ForeignKeyManager, RESTManager):
    _path = "contributor_source"
    _obj_cls = ContributorSource
    _create_attrs = RequiredOptional(required=("source", "contributor"))
    # TODO: figure out if the auth section should be passed in here,

    def get(self, uid=None, params=None):
        # NOTE: the casting allows each object to follow the logic implemented in the
        # MIXIN utils w/o the need to repeating it each time. it also allows customization
        # in each obj
        return cast(ContributorSource, super(ContributorSourceManager, self).get(uid=uid, params=params))
