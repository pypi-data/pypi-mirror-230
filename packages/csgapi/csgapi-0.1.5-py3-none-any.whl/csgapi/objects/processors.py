from typing import cast
from ..base import RESTManager, RESTObject, RequiredOptional
from ..mixin import DeleteMixin, GetMixin, CreateMixin, ListMixin, ObjectDeleteMixin, UpdateMixin, SaveMixin


__all__ = [
    "Processors",
    "ProcessorsManager",
]


class Processors(SaveMixin, ObjectDeleteMixin, RESTObject):
    _id_attr = "uid"
    # pass


class ProcessorsManager(GetMixin, CreateMixin, UpdateMixin, ListMixin, DeleteMixin, RESTManager):
    _path = "processors"
    _obj_cls = Processors
    # TODO: figure out if the auth section should be passed in here,
    # if so we need the func in mixin to refactor attrs before calling POST

    def get(self, uid=None, params=None):
        # NOTE: the casting allows each object to follow the logic implemented in the
        # MIXIN utils w/o the need to repeating it each time. it also allows customization
        # in each obj
        return cast(Processors, super(ProcessorsManager, self).get(uid=uid, params=params))
