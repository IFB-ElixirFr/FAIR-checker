from functools import partial
import functools
import time
import inspect

from parameterized import parameterized
@parameterized.expand([[1,2], [3,4]])
def test(test1, test2):
   print(test1, test2)

def my_decorator(func):
    def wrapper():
        print("Before")
        func()
        print("After")
    return wrapper

@my_decorator
def test_1():
    time.sleep(1)

############################
############################
############################
class Metrics(object):
    pass

def add_metrics(cls, metrics_name):
    def metrics(self):
        print(f"testing FAIR metrics {metrics_name}")

    metrics.__name__ = "test_" + str(metrics_name)
    setattr(cls, metrics.__name__, metrics)

if __name__ == "__main__":
    names = ["f1", "f2", "a2", "a3"]
    for n in names:
        add_metrics(Metrics, n)

    m = Metrics()

    m.test_f1()
    m.test_a3()
    m.test_a4()