import unittest
from pathlib import Path


class FilesAccessTestCase(unittest.TestCase):
    def test_file_access(self):
        # self.assertEqual(True, False)

        base_path = Path(__file__).parent  ## current directory
        print(__file__)
        print(Path(__file__))
        print(Path(__file__).parent)
        file_path = (base_path / "../static/data/jsonldcontext.json").resolve()

        print(file_path)
        n_lines = 0
        with open(file_path) as f:
            for l in f.readlines():
                print(l)
                n_lines += 1
        self.assertGreaterEqual(n_lines, 2500)


if __name__ == "__main__":
    unittest.main()
