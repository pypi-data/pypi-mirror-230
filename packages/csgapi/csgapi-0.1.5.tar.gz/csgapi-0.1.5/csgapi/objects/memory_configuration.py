from typing import cast
from ..base import RESTManager, RESTObject, RequiredOptional
from ..mixin import GetMixin, CreateMixin, UpdateMixin, SaveMixin, ListMixin

__all__ = [
    "MemoryConfiguration",
    "MemoryConfigurationManager",
]


class MemoryConfiguration(SaveMixin, RESTObject):
    _id_attr = "uid"
    # pass


# NOTE: even tho Delete Mixin is integrated, since memory_configuration is a look up table,
# our API does not support DELETE for it
class MemoryConfigurationManager(GetMixin, CreateMixin, UpdateMixin, ListMixin, RESTManager):
    _path = "memory_configurations"
    _obj_cls = MemoryConfiguration
    # TODO: figure out if the auth section should be passed in here,

    def get(self, uid=None, params=None):
        # NOTE: the casting allows each object to follow the logic implemented in the
        # MIXIN utils w/o the need to repeating it each time. it also allows customization
        # in each obj
        return cast(MemoryConfiguration, super(MemoryConfigurationManager, self).get(uid=uid, params=params))
