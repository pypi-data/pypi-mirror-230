from typing import cast
from ..base import RESTManager, RESTObject, RequiredOptional
from ..mixin import DeleteMixin, GetMixin, CreateMixin, UpdateMixin, SaveMixin, ListMixin, ObjectDeleteMixin
from ..utils import handle_client_exception

__all__ = [
    "Green500",
    "Green500Manager",
]


class Green500(SaveMixin, ObjectDeleteMixin, RESTObject):
    _id_attr = "uid"
    # pass


class Green500Manager(GetMixin, CreateMixin, DeleteMixin, UpdateMixin, ListMixin, RESTManager):
    _path = "benchmarks/green500"
    _obj_cls = Green500
    _create_attrs = RequiredOptional(required=("information_source",), optional=("benchmark_type", "green500_rank", "green500_previous_rank",
                                                                                 "top500_rank", "install_year", "publication_date", "power", "power_quality_level",
                                                                                 "power_source", "measured_cores", "total_cores", "optimized_run_hpl",
                                                                                 "optimized_run_peak_power", "submission_type_id", "mflops_per_watt",
                                                                                 "efficiency", "r_max", "r_peak", "n_max", "note"))
    # TODO: figure out if the auth section should be passed in here,
    # if so we need the func in mixin to refactor attrs before calling POST
    _update_attrs = RequiredOptional(required=(), optional=("benchmark_type", "green500_rank", "green500_previous_rank",
                                                            "top500_rank", "information_source", "install_year", "publication_date", "power", "power_quality_level",
                                                            "power_source", "measured_cores", "total_cores", "optimized_run_hpl",
                                                            "optimized_run_peak_power", "submission_type_id", "mflops_per_watt",
                                                            "efficiency", "r_max", "r_peak", "n_max", "note"))

    def get(self, uid=None, params=None):
        # NOTE: the casting allows each object to follow the logic implemented in the
        # MIXIN utils w/o the need to repeating it each time. it also allows customization
        # in each obj
        return cast(Green500, super(Green500Manager, self).get(uid=uid, params=params))
