from typing import cast

from ..types import ForeignKeyManager
from ..base import RESTManager, RESTObject, RequiredOptional
from ..mixin import GetMixin, CreateMixin, UpdateMixin, SaveMixin, ListMixin, DeleteMixin, ObjectDeleteMixin
from ..utils import handle_client_exception


__all__ = [
    "Country",
    "CountryManager",
]


class Country(SaveMixin, ObjectDeleteMixin, RESTObject):
    _id_attr = "uid"
    # pass


class CountryManager(ForeignKeyManager, RESTManager):
    _path = "systems/country"
    _obj_cls = Country
    _create_attrs = RequiredOptional(required=("name",))
    # TODO: figure out if the auth section should be passed in here,
    # if so we need the func in mixin to refactor attrs before calling POST
    _update_attrs = RequiredOptional(required=("name",))

    def get(self, uid=None, params=None):
        # NOTE: the casting allows each object to follow the logic implemented in the
        # MIXIN utils w/o the need to repeating it each time. it also allows customization
        # in each obj
        return cast(Country, super(CountryManager, self).get(uid=uid, params=params))
