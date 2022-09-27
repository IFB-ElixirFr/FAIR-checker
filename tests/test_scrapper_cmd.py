import datetime
import unittest
import sys
import os
import glob


class TestScrapperCMDTool(unittest.TestCase):
    def test_scrapper(self):

        os.system(
            "python app.py --scrapp --urls http://bio.tools/bwa https://bio.tools/FAIR_Search_Engine"
        )

        #### If we will create one dump per execution
        # list_of_files = glob.glob(
        #     "dumps/*.ttl"
        # )  # * means all if need specific format then *.csv
        # latest_file = max(list_of_files, key=os.path.getctime)
        # print("latest created file is ", latest_file)

        # dump_size = os.path.getsize(latest_file)
        # print("dump file size:", dump_size)
        # self.assertGreater(dump_size, 0, "Size dump file is grater than 0!")

        #### If we will create one dump per ressource
        def filesOlderThan(path, day, hour, mins):
            delta = datetime.timedelta(days=day, hours=hour, minutes=mins)
            now = datetime.datetime.now()
            file_list = []
            for root, dirs, files in os.walk(path):
                for a in files:
                    path1 = os.path.join(root, a)
                    c_time = datetime.datetime.fromtimestamp(os.path.getctime(path1))
                    if now - delta < c_time:
                        file_list.append(path1)
            return file_list

        files = filesOlderThan("dumps/", 0, 0, 1)

        print("Number files generated in the last 1 min =", len(files))

        for f in files:
            path = f.split("/")[1]
            list = path.split("$")
            list.remove(f.split("$")[-1])
            res = "/".join(list)
            print("file created for the ressource: ", res)

        self.assertGreaterEqual(len(files), 1, "No file is created in the last 1 min")


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
