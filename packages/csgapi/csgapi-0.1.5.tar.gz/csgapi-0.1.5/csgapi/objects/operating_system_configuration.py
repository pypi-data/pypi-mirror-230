from typing import cast
from ..base import RESTManager, RESTObject, RequiredOptional
from ..mixin import GetMixin, CreateMixin, UpdateMixin, SaveMixin, ListMixin

__all__ = [
    "OperatingSystemConfiguration",
    "OperatingSystemConfigurationManager",
]


class OperatingSystemConfiguration(SaveMixin, RESTObject):
    _id_attr = "uid"
    # pass


# NOTE: even tho Delete Mixin is integrated, since operating_system_configuration is a look up table,
# our API does not support DELETE for it
class OperatingSystemConfigurationManager(GetMixin, CreateMixin, UpdateMixin, ListMixin, RESTManager):
    _path = "operating_system_configurations"
    _obj_cls = OperatingSystemConfiguration
    # TODO: figure out if the auth section should be passed in here,

    def get(self, uid=None, params=None):
        # NOTE: the casting allows each object to follow the logic implemented in the
        # MIXIN utils w/o the need to repeating it each time. it also allows customization
        # in each obj
        return cast(OperatingSystemConfiguration, super(OperatingSystemConfigurationManager, self).get(uid=uid, params=params))
