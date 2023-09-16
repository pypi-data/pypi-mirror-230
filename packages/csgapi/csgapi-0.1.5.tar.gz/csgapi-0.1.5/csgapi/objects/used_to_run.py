from typing import cast
from ..base import RESTManager, RESTObject, RequiredOptional
from ..mixin import GetMixin, CreateMixin, UpdateMixin, SaveMixin, ListMixin
from ..utils import handle_client_exception


__all__ = [
    "UsedToRun",
    "UsedToRunManager",
]


class UsedToRun(SaveMixin, RESTObject):
    _id_attr = "uid"
    # pass


# NOTE: even tho Delete Mixin is integrated, since used_to_run is a look up table,
# our API does not support DELETE for it
class UsedToRunManager(GetMixin, CreateMixin, UpdateMixin, ListMixin, RESTManager):
    _path = "used_to_run"
    _obj_cls = UsedToRun
    _create_attrs = RequiredOptional(required=("benchmark_id",))
    _create_attrs = RequiredOptional(required=("system_id",))
    _create_attrs = RequiredOptional(required=("system_configuration_id",))

    # TODO: figure out if the auth section should be passed in here,
    # if so we need the func in mixin to refactor attrs before calling POST

    def get(self, uid=None, params=None):
        # NOTE: the casting allows each object to follow the logic implemented in the
        # MIXIN utils w/o the need to repeating it each time. it also allows customization
        # in each obj
        return cast(UsedToRun, super(UsedToRunManager, self).get(uid=uid, params=params))
