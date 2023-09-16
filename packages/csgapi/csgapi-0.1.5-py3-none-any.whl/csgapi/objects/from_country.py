from typing import cast
from ..base import RESTManager, RESTObject, RequiredOptional
from ..mixin import GetMixin, CreateMixin, UpdateMixin, SaveMixin, ListMixin

__all__ = [
    "FromCountry",
    "FromCountryManager",
]


class FromCountry(SaveMixin, RESTObject):
    pass


class FromCountryManager(GetMixin, CreateMixin, UpdateMixin, ListMixin, RESTManager):
    _path = "from_country"
    _obj_cls = FromCountry
    _create_attrs = RequiredOptional(required=("contributor", "country"))
    # TODO: figure out if the auth section should be passed in here,

    def get(self, uid=None, params=None):
        # NOTE: the casting allows each object to follow the logic implemented in the
        # MIXIN utils w/o the need to repeating it each time. it also allows customization
        # in each obj
        return cast(FromCountry, super(FromCountryManager, self).get(uid=uid, params=params))
