from typing import cast
from ..base import RESTManager, RESTObject, RequiredOptional
from ..mixin import GetMixin, CreateMixin, UpdateMixin, SaveMixin, ListMixin, DeleteMixin, ObjectDeleteMixin


__all__ = [
    "Resource",
    "ResourceManager",
]


class Resource(SaveMixin, ObjectDeleteMixin, RESTObject):
    _id_attr = "uid"
    # pass


# NOTE: even tho Delete Mixin is integrated, since interconnect_family is a look up table,
# our API does not support DELETE for it
class ResourceManager(GetMixin, CreateMixin, UpdateMixin, ListMixin, DeleteMixin, RESTManager):
    _path = "resource"
    _obj_cls = Resource
    _create_attrs = RequiredOptional(required=("file_name",))
    # TODO: figure out if the auth section should be passed in here,
    # if so we need the func in mixin to refactor attrs before calling POST
    _update_attrs = RequiredOptional(required=("file_name",))

    def get(self, uid=None, params=None):
        # NOTE: the casting allows each object to follow the logic implemented in the
        # MIXIN utils w/o the need to repeating it each time. it also allows customization
        # in each obj
        return cast(Resource, super(ResourceManager, self).get(uid=uid, params=params))
