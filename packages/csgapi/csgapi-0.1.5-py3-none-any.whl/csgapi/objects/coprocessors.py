from typing import cast
from ..base import RESTManager, RESTObject, RequiredOptional
from ..mixin import GetMixin, CreateMixin, UpdateMixin, SaveMixin, ListMixin


__all__ = [
    "Coprocessor",
    "CoprocessorManager",
]


class Coprocessor(SaveMixin, RESTObject):
    _id_attr = "uid"
    # pass


# NOTE: even tho Delete Mixin is integrated, since country is a look up table,
# out API does not dupport DELETE for it
class CoprocessorManager(GetMixin, CreateMixin, UpdateMixin, ListMixin, RESTManager):
    _path = "coprocessor"
    _obj_cls = Coprocessor

    def get(self, uid=None, params=None):
        # NOTE: the casting allows each object to follow the logic implemented in the
        # MIXIN utils w/o the need to repeating it each time. it also allows customization
        # in each obj
        return cast(Coprocessor, super(CoprocessorManager, self).get(uid=uid, params=params))
