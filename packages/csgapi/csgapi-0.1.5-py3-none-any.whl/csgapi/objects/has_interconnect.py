from typing import cast
from ..base import RESTManager, RESTObject, RequiredOptional
from ..mixin import GetMixin, CreateMixin, UpdateMixin, SaveMixin, ListMixin

__all__ = [
    "HasInterconnect",
    "HasInterconnectManager",
]


class HasInterconnect(SaveMixin, RESTObject):
    pass


# NOTE: even tho Delete Mixin is integrated, since has_interconnect is a look up table,
# our API does not support DELETE for it
class HasInterconnectManager(GetMixin, CreateMixin, UpdateMixin, ListMixin, RESTManager):
    _path = "has_interconnect"
    _obj_cls = HasInterconnect
    _create_attrs = RequiredOptional(required=("interconnect_id", "interconnect_configuration_id"))
    # TODO: figure out if the auth section should be passed in here,

    def get(self, uid=None, params=None):
        # NOTE: the casting allows each object to follow the logic implemented in the
        # MIXIN utils w/o the need to repeating it each time. it also allows customization
        # in each obj
        return cast(HasInterconnect, super(HasInterconnectManager, self).get(uid=uid, params=params))
