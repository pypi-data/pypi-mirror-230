from typing import cast
from ..base import RESTManager, RESTObject, RequiredOptional
from ..mixin import GetMixin, CreateMixin, UpdateMixin, SaveMixin, ListMixin


__all__ = [
    "ContributionCategory",
    "ContributionCategoryManager",
]


class ContributionCategory(SaveMixin, RESTObject):
    _id_attr = "uid"
    # pass


# NOTE: even tho Delete Mixin is integrated, since interconnect_family is a look up table,
# our API does not support DELETE for it
class ContributionCategoryManager(GetMixin, CreateMixin, UpdateMixin, ListMixin, RESTManager):
    _path = "contribution_category"
    _obj_cls = ContributionCategory
    _create_attrs = RequiredOptional(required=("name",))
    # TODO: figure out if the auth section should be passed in here,
    # if so we need the func in mixin to refactor attrs before calling POST
    _update_attrs = RequiredOptional(required=("name",))

    def get(self, uid=None, params=None):
        # NOTE: the casting allows each object to follow the logic implemented in the
        # MIXIN utils w/o the need to repeating it each time. it also allows customization
        # in each obj
        return cast(ContributionCategory, super(ContributionCategoryManager, self).get(uid=uid, params=params))
