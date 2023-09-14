import json
import sys
from os.path import abspath, join, dirname

# sys.path.insert(0, join(abspath(dirname(__file__)), "src"))
print(sys.path)
from http_content_parser.generate_api_file import GenerateApiFile


class TestCases:
    def test_curl(self):
        gaf = GenerateApiFile()
        with open("./postman.json", "r") as f:
            json_dict = json.load(f)
        gaf.produce_api_yaml_for_postman(json_dict, "./test.yaml")

    def test_for(self):
        # c = 1
        # for i in range(6):
        #     if i > c:
        #         i += 1
        #         while i < 6:
        #             i += 1
        #     print(str(i))
        data = {"name": "John", "age": 30, "city": "New York"}
        temp = '{    "job_id":{{job_id}},    "product_id": 4,    "local_user_id": 0}'
        temp = json.dumps(data)
        temp = json.loads(temp)
        print(temp)