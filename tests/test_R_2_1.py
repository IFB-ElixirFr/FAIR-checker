import unittest
from metrics.R_1_2_Impl import R_1_2_Impl


class TestingLicenses(unittest.TestCase):
    def test_license_workflowhub(self):
        r21 = R_1_2_Impl("https://workflowhub.eu/workflows/45")
        res = r21.strong_evaluate()
        self.assertEqual(True, res)

    def test_license_dataverse(self):
        r21 = R_1_2_Impl(
            "https://data.inrae.fr/dataset.xhtml?persistentId=doi:10.15454/P27LDX"
        )
        res = r21.strong_evaluate()
        self.assertEqual(False, res)


if __name__ == "__main__":
    unittest.main()
