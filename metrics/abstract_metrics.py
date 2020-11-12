from abc import ABC, abstractmethod

#########################
class AbstractFAIRMetrics(ABC):
    def __init__(self):
        self.name = "My name"

    #common functionality
    def common(self):
        print('In common method of Parent')

    def desc(self):
        print(f'Description of {self.name}')

    @abstractmethod
    def evaluate(self):
        pass

#########################
class F1Impl(AbstractFAIRMetrics):

    def __init__(self):
        self.name = "F1"

    def evaluate(self):
        print("Evaluating F1")

#########################
class R2Impl(AbstractFAIRMetrics):

    def __init__(self):
        self.name = "R2"

    def evaluate(self):
        print("Evaluating R2")

#########################
class FAIRMetricsFactory:
    def get_metrics(self, name):
        if name == 'f1':
            return F1Impl()
        elif name == 'r2':
            return R2Impl()
        else:
            raise ValueError(format)



factory = FAIRMetricsFactory()

metrics = []
#for i in range(1,3):
try:
    metrics.append(factory.get_metrics("f1"))
    metrics.append(factory.get_metrics("r2"))
    #metrics.append(factory.get_metrics("f2"))
except ValueError as e:
    print(f"no metrics implemention for {e}")

for m in metrics:
    m.desc()
    m.evaluate()
