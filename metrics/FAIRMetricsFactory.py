from metrics.F1Impl import F1Impl
from metrics.FAIRMetricsImpl import FAIRMetricsImpl
from metrics.R2Impl import R2Impl


class FAIRMetricsFactory:
    def get_metric(self, name, id, desc, api, principle, creator, created_at, updated_at):
        if name == 'test_f1':
            return F1Impl()
        elif name == 'test_r2':
            return R2Impl()
        else:
            return FAIRMetricsImpl(name, id, desc, api, principle, creator, created_at, updated_at)
