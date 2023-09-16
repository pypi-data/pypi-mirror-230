from typing import cast
from ..base import RESTManager, RESTObject, RequiredOptional
from ..mixin import GetMixin, CreateMixin, UpdateMixin, SaveMixin, ListMixin

__all__ = [
    "SystemConfiguration",
    "SystemConfigurationManager",
]


class SystemConfiguration(SaveMixin, RESTObject):
    _id_attr = "uid"
    # pass


# NOTE: even tho Delete Mixin is integrated, since system_configuration is a look up table,
# our API does not support DELETE for it
class SystemConfigurationManager(GetMixin, CreateMixin, UpdateMixin, ListMixin, RESTManager):
    _path = "system_configurations"
    _obj_cls = SystemConfiguration
    # _create_attrs = RequiredOptional(required=("processor_configuration_id", "memory_configuration_id",
    #                                            "accelerator_configuration_id", "interconnect_configuration_id", "operating_system_configuration_id"))
    # TODO: figure out if the auth section should be passed in here,

    def get(self, uid=None, params=None):
        # NOTE: the casting allows each object to follow the logic implemented in the
        # MIXIN utils w/o the need to repeating it each time. it also allows customization
        # in each obj
        return cast(SystemConfiguration, super(SystemConfigurationManager, self).get(uid=uid, params=params))
