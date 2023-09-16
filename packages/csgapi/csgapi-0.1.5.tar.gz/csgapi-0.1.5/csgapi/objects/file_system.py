from typing import cast
from ..base import RESTManager, RESTObject, RequiredOptional
from ..mixin import GetMixin, CreateMixin, UpdateMixin, SaveMixin, ListMixin
from ..utils import handle_client_exception


__all__ = [
    "FileSystem",
    "FileSystemManager",
]


class FileSystem(SaveMixin, RESTObject):
    _id_attr = "uid"
    # pass


# NOTE: even tho Delete Mixin is integrated, since file_system is a look up table,
# our API does not support DELETE for it
class FileSystemManager(GetMixin, CreateMixin, UpdateMixin, ListMixin, RESTManager):
    _path = "benchmarks/file_system"
    _obj_cls = FileSystem
    _create_attrs = RequiredOptional(required=("name",))
    # TODO: figure out if the auth section should be passed in here,
    # if so we need the func in mixin to refactor attrs before calling POST
    _update_attrs = RequiredOptional(required=("name",))

    def get(self, uid=None, params=None):
        # NOTE: the casting allows each object to follow the logic implemented in the
        # MIXIN utils w/o the need to repeating it each time. it also allows customization
        # in each obj
        return cast(FileSystem, super(FileSystemManager, self).get(uid=uid, params=params))
