from typing import cast
from ..base import RESTManager, RESTObject, RequiredOptional
from ..mixin import GetMixin, CreateMixin, UpdateMixin, SaveMixin, ListMixin
from ..utils import handle_client_exception


__all__ = [
    "OperatingSystem",
    "OperatingSystemManager",
]


class OperatingSystem(SaveMixin, RESTObject):
    _id_attr = "uid"
    # pass


# NOTE: even tho Delete Mixin is integrated, since operating_system is a look up table,
# our API does not support DELETE for it
class OperatingSystemManager(GetMixin, CreateMixin, UpdateMixin, ListMixin, RESTManager):
    _path = "operating_system"
    # TODO: find path name

    _obj_cls = OperatingSystem
    # "os_name", "kernel", "file_system", "os_family", "release_date", "end_of_life_date", "os_version" ))
    _create_attrs = RequiredOptional(required=("name",))
    # NOTE: Check if attributes are required or optional (for both create and update)
    # TODO: figure out if the auth section should be passed in here,
    # if so we need the func in mixin to refactor attrs before calling POST
    # , optional=("kernel", "file_system", "os_family", "release_date", "end_of_life_date", "os_version"))
    _update_attrs = RequiredOptional(required=("name",))
    # TODO: Fix attributes, which are required/optional? Why the discrepancy btwn
    # models.py and the schema?

    def get(self, uid=None, params=None):
        # NOTE: the casting allows each object to follow the logic implemented in the
        # MIXIN utils w/o the need to repeating it each time. it also allows customization
        # in each obj
        return cast(OperatingSystem, super(OperatingSystemManager, self).get(uid=uid, params=params))
