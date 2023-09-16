from typing import cast
from ..base import RESTManager, RESTObject, RequiredOptional
from ..mixin import DeleteMixin, GetMixin, CreateMixin, ListMixin, UpdateMixin, SaveMixin, ObjectDeleteMixin
from ..utils import handle_client_exception

__all__ = [
    "OntologyType",
    "OntologyTypeManager",
]


class OntologyType(SaveMixin, ObjectDeleteMixin, RESTObject):
    _id_attr = "uid"
    # pass


class OntologyTypeManager(GetMixin, CreateMixin, DeleteMixin, UpdateMixin, ListMixin, RESTManager):
    _path = "ontology_type"
    _obj_cls = OntologyType
    _create_attrs = RequiredOptional(required=(), optional=("memory_type", "other_type", "generation", "standard", "module", "standard_type", "clock_rate",
                                     "cycle_time", "transfer_rate", "bandwidth", "cl_trcd_trp", "cas_latency", "voltage", "dimm_pins", "sodimm_pins", "microdimm_pins"))
    # TODO: figure out if the auth section should be passed in here,
    # if so we need the func in mixin to refactor attrs before calling POST
    _update_attrs = RequiredOptional(required=(), optional=("memory_type", "other_type", "generation", "standard", "module", "standard_type", "clock_rate",
                                     "cycle_time", "transfer_rate", "bandwidth", "cl_trcd_trp", "cas_latency", "voltage", "dimm_pins", "sodimm_pins", "microdimm_pins"))

    def get(self, uid=None, params=None):
        # NOTE: the casting allows each object to follow the logic implemented in the
        # MIXIN utils w/o the need to repeating it each time. it also allows customization
        # in each obj
        return cast(OntologyType, super(OntologyTypeManager, self).get(uid=uid, params=params))
