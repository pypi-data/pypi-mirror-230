import sys
from os.path import abspath, join, dirname

# sys.path.insert(0, join(abspath(dirname(__file__)), "src"))
print(sys.path)
from http_content_parser.generate_api_file import GenerateApiFile


class TestCases:
    def test_curl(self):
        gaf = GenerateApiFile()
        gaf.produce_api_yaml_for_curl("./curl.txt", "./test.yaml")

    def test_for():
        c = 1
        for i in range(6):
            if i > c:
                i += 1
                while i < 6:
                    i += 1
            print(str(i))
