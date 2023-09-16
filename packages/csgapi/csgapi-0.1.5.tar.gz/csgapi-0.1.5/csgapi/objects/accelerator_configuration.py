from typing import cast
from ..base import RESTManager, RESTObject, RequiredOptional
from ..mixin import GetMixin, CreateMixin, UpdateMixin, SaveMixin, ListMixin

__all__ = [
    "AcceleratorConfiguration",
    "AcceleratorConfigurationManager",
]


class AcceleratorConfiguration(SaveMixin, RESTObject):
    _id_attr = "uid"
    # pass


# NOTE: even tho Delete Mixin is integrated, since accelerator_configuration is a look up table,
# our API does not support DELETE for it
class AcceleratorConfigurationManager(GetMixin, CreateMixin, UpdateMixin, ListMixin, RESTManager):
    _path = "accelerator_configurations"
    _obj_cls = AcceleratorConfiguration
    # TODO: figure out if the auth section should be passed in here,

    def get(self, uid=None, params=None):
        # NOTE: the casting allows each object to follow the logic implemented in the
        # MIXIN utils w/o the need to repeating it each time. it also allows customization
        # in each obj
        return cast(AcceleratorConfiguration, super(AcceleratorConfigurationManager, self).get(uid=uid, params=params))
