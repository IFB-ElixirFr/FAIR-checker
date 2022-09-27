import logging
import unittest
import sys
import os

from metrics.WebResource import WebResource


class TestScrapperCMDTool(unittest.TestCase):
    def test_scrapper(self):

        os.system("python app.py --scrapp --urls http://bio.tools/bwa")
        dump_size = os.path.getsize("dumps/scrapped_dump.ttl")
        print("dump file size:", dump_size)

        # Test
        list_of_files = glob.glob('/path/to/folder/*') # * means all if need specific format then *.csv
        latest_file = max(list_of_files, key=os.path.getctime)
        print(latest_file)

        self.assertGreater(dump_size, 0, "Size dump file is grater than 0!")


# logging.basicConfig(
#     level=logging.DEBUG,
#     format="[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)-8s %(message)s",
#     datefmt="%Y-%m-%d %H:%M:%S",
# )
# LOGGER = logging.getLogger()
# if not LOGGER.handlers:
#     LOGGER.addHandler(logging.StreamHandler(sys.stdout))

# @unittest.skip("too long")
# class FindabilityTestCase(unittest.TestCase):

#     uri_wf = "https://workflowhub.eu/workflows/45"
#     uri_tool = "https://bio.tools/bwa"
#     wf = None
#     tool = None

#     @classmethod
#     def setUpClass(cls) -> None:
#         super().setUpClass()
#         cls.tool = WebResource(cls.uri_tool)
#         cls.wf = WebResource(cls.uri_wf)

#     @classmethod
#     def tearDownModule(cls) -> None:
#         super().tearDownModule()
#         browser = WebResource.WEB_BROWSER_HEADLESS
#         browser.quit()

#     def test_F1A_biotools_none(self):

#         self.assertEqual(res.get_score(), str(Result.STRONG.value))


# class MyTestCase(unittest.TestCase):

#     @unittest.skip("demonstrating skipping")
#     def test_nothing(self):
#         self.fail("shouldn't happen")

#     @unittest.skipIf(mylib.__version__ < (1, 3),
#                      "not supported in this library version")
#     def test_format(self):
#         # Tests that work for only a certain version of the library.
#         pass

#     @unittest.skipUnless(sys.platform.startswith("win"), "requires Windows")
#     def test_windows_support(self):
#         # windows specific testing code
#         pass

#     def test_maybe_skipped(self):
#         if not external_resource_available():
#             self.skipTest("external resource not available")
#         # test code that depends on the external resource
#         pass

# def suite():
#     suite = unittest.TestSuite()
#     suite.addTest(WidgetTestCase('test_default_widget_size'))
#     suite.addTest(WidgetTestCase('test_widget_resize'))
#     return suite

# if __name__ == '__main__':
#     runner = unittest.TextTestRunner()
#     runner.run(suite())

if __name__ == "__main__":
    unittest.main()
