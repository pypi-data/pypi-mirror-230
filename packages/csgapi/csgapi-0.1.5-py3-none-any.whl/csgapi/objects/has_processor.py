from typing import cast
from ..base import RESTManager, RESTObject, RequiredOptional
from ..mixin import GetMixin, CreateMixin, UpdateMixin, SaveMixin, ListMixin

__all__ = [
    "HasProcessor",
    "HasProcessorManager",
]


class HasProcessor(SaveMixin, RESTObject):
    pass


# NOTE: even tho Delete Mixin is integrated, since has_processor is a look up table,
# our API does not support DELETE for it
class HasProcessorManager(GetMixin, CreateMixin, UpdateMixin, ListMixin, RESTManager):
    _path = "has_processor"
    _obj_cls = HasProcessor
    _create_attrs = RequiredOptional(required=("processor_id", "processor_configuration_id"))
    # TODO: figure out if the auth section should be passed in here,

    def get(self, uid=None, params=None):
        # NOTE: the casting allows each object to follow the logic implemented in the
        # MIXIN utils w/o the need to repeating it each time. it also allows customization
        # in each obj
        return cast(HasProcessor, super(HasProcessorManager, self).get(uid=uid, params=params))
