from typing import cast
from ..base import RESTManager, RESTObject, RequiredOptional
from ..mixin import DeleteMixin, GetMixin, CreateMixin, ListMixin, ObjectDeleteMixin, UpdateMixin, SaveMixin


__all__ = [
    "Spec2006",
    "Spec2006Manager",
]


class Spec2006(SaveMixin, ObjectDeleteMixin, RESTObject):
    _id_attr = "uid"
    # pass


class Spec2006Manager(GetMixin, CreateMixin, UpdateMixin, ListMixin, DeleteMixin, RESTManager):
    _path = "benchmarks/spec2006"
    _obj_cls = Spec2006
    _create_attrs = RequiredOptional(required=("information_source", 'benchmark_type'))
    # TODO: figure out if the auth section should be passed in here,
    # if so we need the func in mixin to refactor attrs before calling POST

    def get(self, uid=None, params=None):
        # NOTE: the casting allows each object to follow the logic implemented in the
        # MIXIN utils w/o the need to repeating it each time. it also allows customization
        # in each obj
        return cast(Spec2006, super(Spec2006Manager, self).get(uid=uid, params=params))
