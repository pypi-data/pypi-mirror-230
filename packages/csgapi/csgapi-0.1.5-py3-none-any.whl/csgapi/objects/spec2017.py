from typing import cast
from ..base import RESTManager, RESTObject, RequiredOptional
from ..mixin import DeleteMixin, GetMixin, CreateMixin, ObjectDeleteMixin, UpdateMixin, SaveMixin, ListMixin


__all__ = [
    "Spec2017",
    "Spec2017Manager",
]


class Spec2017(SaveMixin, ObjectDeleteMixin, RESTObject):
    _id_attr = "uid"
    # pass


class Spec2017Manager(GetMixin, CreateMixin, UpdateMixin, ListMixin, DeleteMixin, RESTManager):
    _path = "benchmarks/spec2017"
    _obj_cls = Spec2017
    _create_attrs = RequiredOptional(required=("information_source", 'benchmark_type'))
    # TODO: figure out if the auth section should be passed in here,
    # if so we need the func in mixin to refactor attrs before calling POST

    def get(self, uid=None, params=None):
        # NOTE: the casting allows each object to follow the logic implemented in the
        # MIXIN utils w/o the need to repeating it each time. it also allows customization
        # in each obj
        return cast(Spec2017, super(Spec2017Manager, self).get(uid=uid, params=params))
