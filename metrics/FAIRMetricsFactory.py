from metrics.F1A_Impl_fm import F1A_Impl_fm
from metrics.F1B_Impl_fm import F1B_Impl_fm
from metrics.F1A_Impl import F1A_Impl
from metrics.F1B_Impl import F1B_Impl
from metrics.F2A_Impl import F2A_Impl
from metrics.F2B_Impl import F2B_Impl
from metrics.FAIRMetricsImpl import FAIRMetricsImpl
from metrics.R_1_1_Impl import R_1_1_Impl
from metrics.FairCheckerExceptions import NotYetImplementedException
from enum import Enum, unique


@unique
class Implem(Enum):
    FAIR_CHECKER = 1
    FAIR_METRICS_API = 2


class FAIRMetricsFactory:
    def get_metric(
        self, name, id, desc, api, principle, creator, created_at, updated_at
    ):
        if name == "test_f1":
            return F1B_Impl()
        elif name == "test_r2":
            return R_1_1_Impl()
        else:
            return FAIRMetricsImpl(
                name, id, desc, api, principle, creator, created_at, updated_at
            )

    @staticmethod
    def get_F1B(web_resource, impl=Implem.FAIR_CHECKER):
        if impl == Implem.FAIR_METRICS_API:
            return F1B_Impl_fm(web_resource)
        else:
            return F1B_Impl(web_resource)

    @staticmethod
    def get_F1A(web_resource, impl=Implem.FAIR_CHECKER):
        if impl == Implem.FAIR_METRICS_API:
            return F1A_Impl_fm(web_resource)
        else:
            return F1A_Impl(web_resource)

    @staticmethod
    def get_F2A(web_resource, impl=Implem.FAIR_CHECKER):
        if impl == Implem.FAIR_METRICS_API:
            raise NotYetImplementedException
        else:
            return F2A_Impl(web_resource)

    @staticmethod
    def get_F2B(web_resource, impl=Implem.FAIR_CHECKER):
        if impl == Implem.FAIR_METRICS_API:
            raise NotYetImplementedException
        else:
            return F2B_Impl(web_resource)
