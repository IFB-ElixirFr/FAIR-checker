import unittest
from metrics.R_1_2_Impl import R_1_2_Impl


class TestingProv(unittest.TestCase):
    def test_prov_workflowhub(self):
        r12 = R_1_2_Impl("https://workflowhub.eu/workflows/45")
        res = r12.evaluate_prov()
        print(res)


if __name__ == "__main__":
    unittest.main()
