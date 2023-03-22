import datetime
import unittest
import sys
import os
import glob


class TestScrapperCMDTool(unittest.TestCase):
    def test_scrapper(self):

        os.system(
            "python app.py --extract-metadata --urls http://bio.tools/bwa https://bio.tools/FAIR_Search_Engine -o metadata_dump"
        )

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

        files = filesOlderThan("metadata_dump/", 0, 0, 1)

        print("Number files generated in the last 1 min =", len(files))

        # for f in files:
        #     path = f.split("/")[1]
        #     list = path.split("$")
        #     list.remove(f.split("$")[-1])
        #     res = "/".join(list)
        #     print("file(s) created for the ressource: ", res)

        self.assertGreaterEqual(len(files), 1, "No file is created in the last 1 min")


if __name__ == "__main__":
    unittest.main()
