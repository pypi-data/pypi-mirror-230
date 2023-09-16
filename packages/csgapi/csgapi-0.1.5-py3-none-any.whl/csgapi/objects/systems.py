from typing import cast
from ..base import RESTManager, RESTObject, RequiredOptional
from ..mixin import GetMixin, CreateMixin, UpdateMixin, SaveMixin, ListMixin, ObjectDeleteMixin, DeleteMixin
from ..utils import handle_client_exception

__all__ = [
    "Systems",
    "SystemsManager",
]


class Systems(SaveMixin, ObjectDeleteMixin, RESTObject):
    _id_attr = "uid"
    # pass


class SystemsManager(GetMixin, CreateMixin, UpdateMixin, ListMixin, DeleteMixin, RESTManager):
    _path = "systems"
    _obj_cls = Systems
    _create_attrs = RequiredOptional(required=(), optional=("moniker", "system_model",
                                                            "system_family_id", "architecture_id", "system_manufacturer_id", "computer",
                                                            "site", "application_id", "country_id", "region_id", "continent_id", "segment_id",
                                                            "system_address", "latitude", "longitude"))
    # TODO: figure out if the auth section should be passed in here,
    # if so we need the func in mixin to refactor attrs before calling POST
    _update_attrs = RequiredOptional(required=(), optional=("moniker", "system_model",
                                                            "system_family_id", "architecture_id", "system_manufacturer_id", "computer",
                                                            "site", "application_id", "country_id", "region_id", "continent_id", "segment_id",
                                                            "system_address", "latitude", "longitude"))

    def get(self, uid=None, params=None):
        # NOTE: the casting allows each object to follow the logic implemented in the
        # MIXIN utils w/o the need to repeating it each time. it also allows customization
        # in each obj
        return cast(Systems, super(SystemsManager, self).get(uid=uid, params=params))
