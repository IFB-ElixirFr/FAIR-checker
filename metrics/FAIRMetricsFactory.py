from metrics.F1A_Impl_fm import F1A_Impl_fm
from metrics.F1B_Impl_fm import F1B_Impl_fm
from metrics.F1A_Impl import F1A_Impl
from metrics.F1B_Impl import F1B_Impl
from metrics.F2A_Impl import F2A_Impl
from metrics.F2B_Impl import F2B_Impl
from metrics.A11_Impl import A11_Impl
from metrics.I1_Impl import I1_Impl
from metrics.I1A_Impl import I1A_Impl
from metrics.I1B_Impl import I1B_Impl
from metrics.I2_Impl import I2_Impl
from metrics.I2A_Impl import I2A_Impl
from metrics.I2B_Impl import I2B_Impl
from metrics.I3_Impl import I3_Impl
from metrics.FAIRMetricsImpl import FAIRMetricsImpl
from metrics.R11_Impl import R11_Impl
from metrics.R12_Impl import R12_Impl
from metrics.R13_Impl import R13_Impl
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
        return FAIRMetricsImpl(
            name, id, desc, api, principle, creator, created_at, updated_at
        )

    @staticmethod
    def get_FC_metrics():
        fc_metrics_list = {
            F1A_Impl().get_name(): F1A_Impl(),
            F1B_Impl().get_name(): F1B_Impl(),
            F2A_Impl().get_name(): F2A_Impl(),
            F2B_Impl().get_name(): F2B_Impl(),
            A11_Impl().get_name(): A11_Impl(),
            I1_Impl().get_name(): I1_Impl(),
            I2_Impl().get_name(): I2_Impl(),
            I3_Impl().get_name(): I3_Impl(),
            R11_Impl().get_name(): R11_Impl(),
            R12_Impl().get_name(): R12_Impl(),
            R13_Impl().get_name(): R13_Impl(),
        }
        return fc_metrics_list

    @staticmethod
    def get_F1B(web_resource=None, impl=Implem.FAIR_CHECKER):
        if impl == Implem.FAIR_METRICS_API:
            return F1B_Impl_fm(web_resource)
        else:
            return F1B_Impl(web_resource)

    @staticmethod
    def get_F1A(web_resource=None, impl=Implem.FAIR_CHECKER):
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

    @staticmethod
    def get_A11(web_resource, impl=Implem.FAIR_CHECKER):
        if impl == Implem.FAIR_METRICS_API:
            raise NotYetImplementedException
        else:
            return A11_Impl(web_resource)

    @staticmethod
    def get_I1(web_resource, impl=Implem.FAIR_CHECKER):
        if impl == Implem.FAIR_METRICS_API:
            raise NotYetImplementedException
        else:
            return I1_Impl(web_resource)

    @staticmethod
    def get_I1A(web_resource, impl=Implem.FAIR_CHECKER):
        if impl == Implem.FAIR_METRICS_API:
            raise NotYetImplementedException
        else:
            return I1A_Impl(web_resource)

    @staticmethod
    def get_I1B(web_resource, impl=Implem.FAIR_CHECKER):
        if impl == Implem.FAIR_METRICS_API:
            raise NotYetImplementedException
        else:
            return I1B_Impl(web_resource)

    @staticmethod
    def get_I2(web_resource, impl=Implem.FAIR_CHECKER):
        if impl == Implem.FAIR_METRICS_API:
            raise NotYetImplementedException
        else:
            return I2_Impl(web_resource)

    @staticmethod
    def get_I2A(web_resource, impl=Implem.FAIR_CHECKER):
        if impl == Implem.FAIR_METRICS_API:
            raise NotYetImplementedException
        else:
            return I2A_Impl(web_resource)

    @staticmethod
    def get_I2B(web_resource, impl=Implem.FAIR_CHECKER):
        if impl == Implem.FAIR_METRICS_API:
            raise NotYetImplementedException
        else:
            return I2B_Impl(web_resource)

    @staticmethod
    def get_I3(web_resource, impl=Implem.FAIR_CHECKER):
        if impl == Implem.FAIR_METRICS_API:
            raise NotYetImplementedException
        else:
            return I3_Impl(web_resource)

    @staticmethod
    def get_R11(web_resource, impl=Implem.FAIR_CHECKER):
        if impl == Implem.FAIR_METRICS_API:
            raise NotYetImplementedException
        else:
            return R11_Impl(web_resource)

    @staticmethod
    def get_R12(web_resource, impl=Implem.FAIR_CHECKER):
        if impl == Implem.FAIR_METRICS_API:
            raise NotYetImplementedException
        else:
            return R12_Impl(web_resource)

    @staticmethod
    def get_R13(web_resource, impl=Implem.FAIR_CHECKER):
        if impl == Implem.FAIR_METRICS_API:
            raise NotYetImplementedException
        else:
            return R13_Impl(web_resource)
