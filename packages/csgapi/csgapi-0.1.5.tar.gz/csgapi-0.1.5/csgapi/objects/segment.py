from typing import cast
from ..base import RESTManager, RESTObject, RequiredOptional
from ..mixin import GetMixin, CreateMixin, UpdateMixin, SaveMixin, ListMixin


__all__ = [
    "Segment",
    "SegmentManager",
]


class Segment(SaveMixin, RESTObject):
    _id_attr = "uid"
    # pass


# NOTE: even tho Delete Mixin is integrated, since country is a look up table,
# out API does not dupport DELETE for it
class SegmentManager(GetMixin, CreateMixin, UpdateMixin, ListMixin, RESTManager):
    _path = "systems/segment"
    _obj_cls = Segment
    _create_attrs = RequiredOptional(required=("name",))
    # TODO: figure out if the auth section should be passed in here,
    # if so we need the func in mixin to refactor attrs before calling POST
    _update_attrs = RequiredOptional(required=("name",))

    def get(self, uid=None, params=None):
        # NOTE: the casting allows each object to follow the logic implemented in the
        # MIXIN utils w/o the need to repeating it each time. it also allows customization
        # in each obj
        return cast(Segment, super(SegmentManager, self).get(uid=uid, params=params))
