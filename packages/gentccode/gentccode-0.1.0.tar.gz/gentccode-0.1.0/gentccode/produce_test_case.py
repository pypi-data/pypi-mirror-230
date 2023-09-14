import copy
from gentccode.merge_api import merge_api_params
import requests
import yaml
import json
from gentccode.generate_case_code import GenerateCaseCode
from gentccode.read_swagger_rule import NoneRule, SwaggerRule

from http_content_parser.generate_api_file import GenerateApiFile


class ProduceTestCase(object):
    def __init__(self) -> None:
        self.gcc = GenerateCaseCode()
        self.gaf = GenerateApiFile()

    def produce_case_by_yaml_for_postman(
        self, json_file_path, yaml_file, case_code_file
    ):
        with open(json_file_path, "r") as f:
            json_dict = json.load(f)
        self.gaf.produce_api_yaml_for_postman(json_dict, yaml_file)
        none_rule = NoneRule()
        self.gcc.produce_code_for_api_yaml(
            yaml_file_path=yaml_file,
            case_code_file_path=case_code_file,
            rule_tool=none_rule,
        )

    def produce_case_by_yaml_for_swagger2(
        self, swagger_json_path, yaml_file, case_code_file
    ):
        # 读取 doc.json 文件
        with open(swagger_json_path, "r") as f:
            swagger2_dict = json.load(f)
        self.gaf.produce_api_yaml_for_swagger2(swagger2_dict, yaml_file)
        none_rule = NoneRule()
        self.gcc.produce_code_for_api_yaml(
            yaml_file_path=yaml_file,
            case_code_file_path=case_code_file,
            rule_tool=none_rule,
        )

    def produce_case_by_yaml_for_curl(
        self, curl_file, yaml_file, case_code_file, curl_filter=None
    ):
        self.gaf.produce_api_yaml_for_curl(curl_file, yaml_file, curl_filter)
        none_rule = NoneRule()
        self.gcc.produce_code_for_api_yaml(
            yaml_file_path=yaml_file,
            case_code_file_path=case_code_file,
            rule_tool=none_rule,
        )

    #
    # unique_char 是防止一个接口生成多个case时方法名重复的问题
    def produce_case_by_curl(
        self,
        param_list,
        curl_file,
        test_case_file,
        unique_char=False,
        **kwargs,
    ):
        # read from curl
        http_payloads = self.gaf.convert_curl_data_to_model(curl_file_path=curl_file)
        # modify api's param
        new_payloads = []
        for p in param_list:
            for payload in http_payloads:
                temp = copy.deepcopy(payload)
                temp.body = p
                new_payloads.append(temp)
        # generate code
        self.gcc.produce_code(
            req_datas=new_payloads,
            test_case_file_path=test_case_file,
            unique_char=unique_char,
            **kwargs
        )

    def produce_merged_case_for_openapi_and_curl(self, curl_file_path):
        # 从curl文件中生成yaml
        curl_yaml_file_path = "script/generated_result/curl_merge.yaml"
        with open(curl_yaml_file_path, "w") as f:
            f.write("")  # 先清空之前的内容
        self.gaf.produce_api_yaml_for_curl(
            curl_file=curl_file_path, yaml_file=curl_yaml_file_path
        )
        with open(curl_yaml_file_path, "r") as f:
            data2 = yaml.safe_load(f)
        api_dict = dict(data2)

        # 从rap上获取openapi
        openapi_dict = self.download_openapi3_json()
        openapi_yaml_file_path = "script/generated_result/openapi_merge.yaml"
        with open(openapi_yaml_file_path, "w") as f:
            f.write("")  # 先清空之前的内容
        self.gaf.produce_api_yaml_for_openapi3(
            openapi_dict=openapi_dict, yaml_file=openapi_yaml_file_path
        )
        with open(openapi_yaml_file_path, "r") as f:
            data = yaml.safe_load(f)
        openapi_dict = dict(data)

        # 合并上面两个yaml,生成合并后yaml
        res = merge_api_params(openapi_dict, api_dict)
        print(json.dumps(res[1]))
        merged_yaml_path = "./script/generated_result/merged.yaml"
        with open(merged_yaml_path, "w") as f:
            yaml.dump(res[0], f, encoding="UTF-8")

        # 根据merge后的yaml,生成用例代码
        # case_file_path = 'testcase/swagger/test_toc_swagger.py'
        case_file_path = "./script/generated_result/openapi_curl.py"
        swagger_rule = SwaggerRule()
        self.gcc.produce_code_for_api_yaml(
            case_code_file_path=case_file_path,
            yaml_file_path=merged_yaml_path,
            rule_tool=swagger_rule,
            split_respone_assert=True,
        )

    def produce_merged_case_for_swagger_and_curl(self, curl_file_path):
        # 从curl文件中生成yaml
        curl_yaml_file_path = "script/generated_result/curl_merge.yaml"
        with open(curl_yaml_file_path, "w") as f:
            f.write("")  # 先清空之前的内容
        self.gaf.produce_api_yaml_for_curl(
            curl_file=curl_file_path, yaml_file=curl_yaml_file_path
        )
        with open(curl_yaml_file_path, "r") as f:
            data2 = yaml.safe_load(f)
        api_dict = dict(data2)

        # 从swagger中生成yaml
        with open("doc.json", "r") as f:
            swagger2_dict = json.load(f)
        swagger_yaml_file_path = "script/generated_result/swagger_merge.yaml"
        with open(swagger_yaml_file_path, "w") as f:
            f.write("")  # 先清空之前的内容
        self.gaf.produce_api_yaml_for_swagger2(
            swagger2_dict=swagger2_dict, yaml_file=swagger_yaml_file_path
        )
        with open(swagger_yaml_file_path, "r") as f:
            data = yaml.safe_load(f)
        swagger_dict = dict(data)

        # 合并上面两个yaml,生成合并后yaml
        res = merge_api_params(swagger_dict, api_dict)
        print(json.dumps(res[1]))
        merged_yaml_path = "./script/generated_result/merged.yaml"
        with open(merged_yaml_path, "w") as f:
            yaml.dump(res[0], f)

        # 根据merge后的yaml,生成用例代码
        case_file_path = "testcase/swagger/test_toc_swagger.py"
        swagger_rule = SwaggerRule()
        self.gcc.produce_code_for_api_yaml(
            case_code_file_path=case_file_path,
            yaml_file_path=merged_yaml_path,
            rule_tool=swagger_rule,
            split_respone_assert=True,
        )

    def download_swagger_json(self, url):
        d = {}
        try:
            d = requests.get(url=url).json()
        except Exception as ex:
            print(ex)
        return d

    def download_openapi3_json(
        self, url=""
    ):
        d = {}
        h = {
            "Cookie": ""
        }
        d = requests.get(url=url, headers=h).json()
        if not d.get("isOk", True):
            raise Exception("get openapi result error")
        return d


if __name__ == "__main__":
    # 生成的接口信息会保存到这个文件中
    api_yaml_file_path = "./script/generated_result/api_template.yaml"
    # 生成的接口代码会保存到这个文件中
    case_file_path = "./script/generated_result/case_template.py"
    curl_file_path = "./script/generated_result/curls.txt"

    ptc = ProduceTestCase()
    ptc.produce_case_by_yaml_for_curl(
        curl_file_path, api_yaml_file_path, case_file_path
    )
