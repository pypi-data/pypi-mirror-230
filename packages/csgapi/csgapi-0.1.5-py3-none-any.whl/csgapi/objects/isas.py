from typing import cast
from ..base import RESTManager, RESTObject, RequiredOptional
from ..mixin import DeleteMixin, GetMixin, CreateMixin, ListMixin, UpdateMixin, SaveMixin, ObjectDeleteMixin
from ..utils import handle_client_exception

__all__ = [
    "Isas",
    "IsasManager",
]


class Isas(SaveMixin, ObjectDeleteMixin, RESTObject):
    _id_attr = "uid"
    # pass


class IsasManager(GetMixin, CreateMixin, DeleteMixin, UpdateMixin, ListMixin, RESTManager):
    _path = "isas"
    _obj_cls = Isas
    _create_attrs = RequiredOptional(required=("name",), optional=("year", "note", "Designer_id"))
    # TODO: figure out if the auth section should be passed in here,
    # if so we need the func in mixin to refactor attrs before calling POST
    _update_attrs = RequiredOptional(required=("name",), optional=("year", "note", "Designer_id"))

    def get(self, uid=None, params=None):
        # NOTE: the casting allows each object to follow the logic implemented in the
        # MIXIN utils w/o the need to repeating it each time. it also allows customization
        # in each obj
        return cast(Isas, super(IsasManager, self).get(uid=uid, params=params))
