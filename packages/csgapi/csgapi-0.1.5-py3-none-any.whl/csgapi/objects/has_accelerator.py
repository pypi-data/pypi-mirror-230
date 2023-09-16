from typing import cast
from ..base import RESTManager, RESTObject, RequiredOptional
from ..mixin import GetMixin, CreateMixin, UpdateMixin, SaveMixin, ListMixin

__all__ = [
    "HasAccelerator",
    "HasAcceleratorManager",
]


class HasAccelerator(SaveMixin, RESTObject):
    pass


# NOTE: even tho Delete Mixin is integrated, since has_accelerator is a look up table,
# our API does not support DELETE for it
class HasAcceleratorManager(GetMixin, CreateMixin, UpdateMixin, ListMixin, RESTManager):
    _path = "has_accelerator"
    _obj_cls = HasAccelerator
    _create_attrs = RequiredOptional(required=("accelerator_id", "accelerator_configuration_id"))
    # TODO: figure out if the auth section should be passed in here,

    def get(self, uid=None, params=None):
        # NOTE: the casting allows each object to follow the logic implemented in the
        # MIXIN utils w/o the need to repeating it each time. it also allows customization
        # in each obj
        return cast(HasAccelerator, super(HasAcceleratorManager, self).get(uid=uid, params=params))
