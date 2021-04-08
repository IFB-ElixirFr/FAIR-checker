import unittest
from pathlib import Path


class MyTestCase(unittest.TestCase):
    def test_something(self):
        #self.assertEqual(True, False)

        base_path = Path(__file__).parent ## current directory
        print(__file__)
        print(Path(__file__))
        print(Path(__file__).parent)
        file_path = (base_path / "../static/data/jsonldcontext.json").resolve()

        print(file_path)
        with open(file_path) as f:
            for l in f.readlines():
                print(l)


if __name__ == '__main__':
    unittest.main()
