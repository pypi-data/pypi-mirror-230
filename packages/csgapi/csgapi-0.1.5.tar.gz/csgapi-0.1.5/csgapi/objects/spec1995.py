from typing import cast
from ..base import RESTManager, RESTObject, RequiredOptional
from ..mixin import DeleteMixin, GetMixin, CreateMixin, ListMixin, ObjectDeleteMixin, UpdateMixin, SaveMixin


__all__ = [
    "Spec1995",
    "Spec1995Manager",
]


class Spec1995(SaveMixin, ObjectDeleteMixin, RESTObject):
    _id_attr = "uid"
    # pass


class Spec1995Manager(GetMixin, CreateMixin, UpdateMixin, ListMixin, DeleteMixin, RESTManager):
    _path = "benchmarks/spec1995"
    _obj_cls = Spec1995
    _create_attrs = RequiredOptional(required=("information_source", 'benchmark_type'))
    # TODO: figure out if the auth section should be passed in here,
    # if so we need the func in mixin to refactor attrs before calling POST

    def get(self, uid=None, params=None):
        # NOTE: the casting allows each object to follow the logic implemented in the
        # MIXIN utils w/o the need to repeating it each time. it also allows customization
        # in each obj
        return cast(Spec1995, super(Spec1995Manager, self).get(uid=uid, params=params))
