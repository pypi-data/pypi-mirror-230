# -*- coding: UTF-8 -*-
from gentccode.merge_api import SplitKV
from gentccode.merge_api import ResponseSplitKV
from gentccode.merge_api import SplitAssertResponse
import yaml
import json
from gentccode.read_swagger_rule import BaseRule, NoneRule
from http_content_parser.param_util import ParamUtil
from http_content_parser.req_data import ReqData


class GenerateCaseCode(object):
    def __init__(self) -> None:
        self.CHAR_SPACE_8 = "        "
        self.CHAR_SPACE_4 = "    "

    def produce_code_for_api_yaml(
        self,
        yaml_file_path,
        case_code_file_path,
        rule_tool: BaseRule,
        split_respone_assert=False,
    ):
        with open(yaml_file_path, "r") as f:
            yaml_dict = yaml.safe_load(f)
        with open(case_code_file_path, "wt") as f:
            f.write(self.get_import_and_class_setup_str())
        for k, v in yaml_dict.items():
            req_data = ReqData(v)
            req_data.temp_api_label = k
            # 根据sql_rule的结果来自动判断是否进行加载rule
            sql_rule = rule_tool.get_api_mysql_method(api_name=k)
            with open(case_code_file_path, "at") as f:
                f.write(
                    self.edit_method_content(
                        req_data,
                        has_payload_assgin=True,
                        has_response_assert=True,
                        split_respone_assert=split_respone_assert,
                        has_global_var=True,
                        reset_header=True,
                        **sql_rule,
                    )
                )

    @DeprecationWarning
    def produce_code_for_api_yaml_old(
        self,
        yaml_file_path,
        case_code_file_path,
        rule_tool: BaseRule,
        split_respone_assert=False,
    ):
        with open(yaml_file_path, "r") as f:
            yaml_dict = yaml.safe_load(f)
        with open(case_code_file_path, "wt") as f:
            f.write(self.get_import_and_class_setup_str())
        for k, v in yaml_dict.items():
            req_data = ReqData(v)
            sql_rule = rule_tool.get_api_mysql_method(api_name=k)
            req_data.temp_api_label = k
            with open(case_code_file_path, "at") as f:
                if sql_rule:
                    f.write(
                        self.get_request_method_str(
                            req_data,
                            has_payload_assgin=True,
                            has_response_assert=True,
                            split_respone_assert=split_respone_assert,
                            has_global_var=True,
                            reset_header=True,
                            **sql_rule,
                        )
                    )
                else:
                    f.write(
                        self.get_request_method_str(
                            req_data,
                            has_payload_assgin=True,
                            has_response_assert=True,
                            split_respone_assert=split_respone_assert,
                            has_global_var=True,
                            reset_header=True,
                        )
                    )

    def produce_code(
        self,
        req_datas: list[ReqData],
        test_case_file_path: str,
        split_respone_assert=False,
        unique_char=False,
        **kwargs,
    ):
        with open(test_case_file_path, "wt") as f:
            f.write(self.get_import_and_class_setup_str())
        n = 0
        for req_data in req_datas:
            with open(test_case_file_path, "at") as f:
                # TODO 后缀只支持接从0递增的数字,后续考虑支持任意字符
                if unique_char:
                    s = "_" + str(n)
                    cases = self.edit_method_content(
                        req_data,
                        has_payload_assgin=True,
                        has_response_assert=True,
                        split_respone_assert=split_respone_assert,
                        reset_header=True,
                        unique_char=s,
                        **kwargs,
                    )
                    n += 1
                else:
                    cases = self.edit_method_content(
                        req_data,
                        has_payload_assgin=True,
                        has_response_assert=True,
                        split_respone_assert=split_respone_assert,
                        reset_header=True,
                        **kwargs,
                    )
                f.write(cases)

    def convert_api_str(self, api_str):
        return api_str.replace("-", "_").replace("{", "").replace("}", "")

    # return method part str, includes http request code
    @DeprecationWarning
    def get_request_method_str(
        self,
        req_data: ReqData,
        has_payload_assgin=False,
        has_response_assert=False,
        split_respone_assert=False,
        has_global_var=False,
        reset_header=False,
        **kwargs,
    ) -> str:
        space_str_4 = self.CHAR_SPACE_4
        space_str_8 = self.CHAR_SPACE_8
        payload = ""
        response_assert = ""
        response_global = ""
        header_reset_str = ""
        mysql_str = ""
        unique_char = ""
        if has_payload_assgin:
            kv_fix_list = ["request_model.body", "", "", ""]
            payload = self.get_payload_with_assigin_value_str(
                param_dict=req_data.body, kv_fix_list=kv_fix_list, middle_char="="
            )
        if has_response_assert:
            kv_fix_list = ["assert type(response", ")", "", ""]
            if split_respone_assert:
                response_assert = self.get_every_assert_method_str2(
                    param_dict=req_data.response,
                    kv_fix_list=kv_fix_list,
                    middle_char=" == ",
                    req_data=req_data,
                )
            else:
                response_assert = self.get_assert_response_content_str2(
                    req_data.response, kv_fix_list, " == "
                )
            response_assert = (
                f'{space_str_8}assert response.get("error", -99) == 0\n'
                + response_assert
            )
        if has_global_var:
            response_global = f"{space_str_8}global response\n"
        if reset_header:
            header_reset_str = space_str_8 + "request_model.header = {}\n"
        for k, v in kwargs.items():
            if k == "add_mysql_method":
                mysql_str = space_str_8 + f"self.toc_sql.{v}()\n"
            if k == "unique_char":
                unique_char = v

        method_str = (
            f"{space_str_4}@allure.title('{req_data.method}: {req_data.path}{unique_char}')\n"
            + f"{space_str_4}def test_case_{req_data.temp_api_label.replace('-', '_').replace('{','').replace('}','')}{unique_char}(self):\n"
            + f"{space_str_8}# 读取yaml中所有api数据,转换为dict\n"
            + f"{space_str_8}api_info_in_yaml = ParseUtil.parse_api_info_from_yaml(self.api_yaml_path)\n"
            + f"{space_str_8}# 获取指定api信息\n"
            + f"{space_str_8}request_model = api_info_in_yaml['{req_data.temp_api_label}']\n"
            + f"{space_str_8}# 编辑header\n"
            + header_reset_str
            + f"{space_str_8}request_model.header.update(self.header_auth)\n"
            + f"{space_str_8}# 编辑payload\n"
            + payload
            + f"{space_str_8}# 预置数据\n"
            + mysql_str
            + f"{space_str_8}# 发送请求\n"
            + response_global
            + f"{space_str_8}response = HttpUtil.request_with_yaml(request_model, service_host_ip_label=self.service_ip_label)\n"
            + f"{space_str_8}# 校验返回信息\n"
            + f"{space_str_8}assert type(response) == dict\n"
            + response_assert
        )
        return method_str

    def edit_method_content(
        self, req_data: ReqData, split_respone_assert=False, **kwargs
    ):
        space_8 = self.CHAR_SPACE_8
        edit_payload_str = ""
        edit_payload_str_before = ""
        edit_payload_str_middle = ""
        assert_response_str = ""
        send_request_str = ""
        edit_header_str = ""
        preset_data_str = ""
        method_name_suffix = ""
        assert_response_str_after = ""
        for k, v in kwargs.items():
            if k == "add_mysql_method":
                preset_data_str += space_8 + f"self.toc_sql.{v}()\n"
            elif k == "edit_payload_str_before":
                edit_payload_str_before += f"{space_8}{v}\n"
            elif k == "unique_char":
                method_name_suffix += v
            elif k == "has_payload_assgin":
                if v:
                    kv_fix_list = ["request_model.body", "", "", ""]
                    edit_payload_str_middle += self.get_payload_with_assigin_value_str(
                        param_dict=req_data.body,
                        kv_fix_list=kv_fix_list,
                        middle_char="=",
                    )
            elif k == "has_response_assert":
                if v:
                    kv_fix_list = ["assert type(response", ")", "", ""]
                    if split_respone_assert:
                        assert_response_str += self.get_every_assert_method_str2(
                            param_dict=req_data.response,
                            kv_fix_list=kv_fix_list,
                            middle_char=" == ",
                            req_data=req_data,
                        )
                        send_request_str += f"{space_8}global response\n"
                    else:
                        assert_response_str += self.get_assert_response_content_str2(
                            req_data.response, kv_fix_list, " == "
                        )
                    assert_response_str += (
                        f'{space_8}assert response.get("error", -99) == 0\n'
                    )
            elif k == "reset_header":
                if v:
                    edit_header_str += space_8 + "request_model.header = {}\n"
            elif k == "assert_response_str_after":
                assert_response_str_after += f"{space_8}{v}\n"

        edit_payload_str = edit_payload_str_before + edit_payload_str_middle
        assert_response_str += assert_response_str_after
        return self.get_method_content_str(
            req_data=req_data,
            method_name_suffix=method_name_suffix,
            preset_data_str=preset_data_str,
            edit_header_str=edit_header_str,
            send_request_str=send_request_str,
            assert_response_str=assert_response_str,
            edit_payload_str=edit_payload_str,
        )

    def get_method_content_str(self, req_data: ReqData, **kwargs) -> str:
        space_4 = self.CHAR_SPACE_4
        space_8 = self.CHAR_SPACE_8
        edit_payload = ""
        assert_response = ""
        send_request = ""
        edit_header = ""
        preset_data = ""
        method_name_suffix = ""
        for arg_name, arg_value in kwargs.items():
            if arg_name == "method_name_suffix":
                method_name_suffix = arg_value
            elif arg_name == "edit_header_str":
                edit_header = arg_value
            elif arg_name == "assert_response_str":
                assert_response = arg_value
            elif arg_name == "preset_data_str":
                preset_data = arg_value
            elif arg_name == "send_request_str":
                send_request = arg_value
            elif arg_name == "edit_payload_str":
                edit_payload = arg_value
            else:
                print(f"arg: {arg_name} is invalid")

        method_str = (
            f"{space_4}@allure.title('{req_data.method}: {req_data.path}{method_name_suffix}')\n"
            + f"{space_4}def test_case_{req_data.temp_api_label.replace('-', '_').replace('{','').replace('}','')}{method_name_suffix}(self):\n"
            + f"{space_8}# 读取yaml中所有api数据,转换为dict\n"
            + f"{space_8}api_info_in_yaml = ParseUtil.parse_api_info_from_yaml(self.api_yaml_path)\n"
            + f"{space_8}# 获取指定api信息\n"
            + f"{space_8}request_model = api_info_in_yaml['{req_data.temp_api_label}']\n"
            + f"{space_8}# 编辑header\n"
            + edit_header
            + f"{space_8}request_model.header.update(self.header_auth)\n"
            + f"{space_8}# 编辑payload\n"
            + edit_payload
            + f"{space_8}# 预置数据\n"
            + preset_data
            + f"{space_8}# 发送请求\n"
            + send_request
            + f"{space_8}response = HttpUtil.request_with_yaml(request_model, service_host_ip_label=self.service_ip_label)\n"
            + f"{space_8}# 校验返回信息\n"
            + f"{space_8}assert type(response) == dict\n"
            + assert_response
        )
        return method_str

    # return method part str, split assert code to new method.
    def get_every_assert_method_str2(
        self, param_dict, kv_fix_list, middle_char, req_data: ReqData
    ) -> str:
        split_kv = SplitAssertResponse()
        return self._get_split_kv_str(
            param_dict, split_kv, kv_fix_list, middle_char, req_data
        )

    # return response assert part code, includes response all body's key and value
    def get_assert_response_content_str2(
        self, param_dict, kv_fix_list, middle_char, method_str=""
    ):
        split_kv = ResponseSplitKV()
        return self._get_split_kv_str(
            param_dict, split_kv, kv_fix_list, middle_char, method_str
        )

    def _get_split_kv_str(self, param_dict, split_kv: SplitKV, *args):
        response_str = ""
        if param_dict:
            if isinstance(param_dict, str):
                try:
                    param_dict = json.loads(param_dict.replace("\\n", ""))
                except:
                    print(f"param type is not json str.\n{param_dict}")
                    return response_str
            if isinstance(param_dict, (dict, list)):
                temp = json.dumps(param_dict).replace("\\n", "")
                param_dict = json.loads(temp)
                param_assign_value_list = ParamUtil.split_swagger_param_and_type(
                    param_dict, nontype=False
                )
                assigin_list = split_kv.splice_param_kv(param_assign_value_list, *args)
                response_str = "".join(assigin_list)
            else:
                print(f"param type is error: {type(param_dict)}\n{param_dict}")
        return response_str

    # return class top part str, includes import and class definition
    def get_import_and_class_setup_str(self) -> str:
        space_str_4 = self.CHAR_SPACE_4
        space_str_8 = self.CHAR_SPACE_8
        setup_class_str = (
            "from testcase.toc.toc_auth.user_auth import TocUserUtil\n"
            + "from utils.base.http_util import HttpUtil\n"
            + "from testcase.swagger.sql.prepare_sql_for_case import TocSwaggerSql\n"
            + "from utils.base.parse import ParseUtil\n"
            + "from utils.business.path_util import PathUtil\n"
            + "import allure\n"
            + "class TestCases(object):\n"
            + f"{space_str_4}def setup_class(self):\n"
            + f"{space_str_8}"
            + "self.api_token = TocUserUtil.get_user_api_token('subot1@shopee.com')\n"
            + f"{space_str_8}"
            + "self.service_ip_label = 'toc'\n"
            + f"{space_str_8}"
            + "self.header_auth = {'Authorization': self.api_token}\n"
            + f"{space_str_8}#-----------------------------------------------------------\n"
            + f"{space_str_8}# 替换成自己业务api的yaml文件的path\n"
            + f"{space_str_8}self.api_yaml_path = PathUtil.get_api_template_yaml_path()\n"
            + f"{space_str_8}#-----------------------------------------------------------\n"
            + f"{space_str_8}self.toc_sql = TocSwaggerSql()\n"
        )
        return setup_class_str

    # return payload part str, includes assigin payload's key to value
    def get_payload_with_assigin_value_str(
        self, param_dict, kv_fix_list, middle_char
    ) -> str:
        payload_assigin_str = ""
        if param_dict:
            if isinstance(param_dict, str):
                try:
                    param_dict = json.loads(param_dict.replace("\\n", ""))
                except:
                    print(f"api body type is not json str.\n{param_dict}")
                    return payload_assigin_str
            if isinstance(param_dict, (dict, list)):
                temp = json.dumps(param_dict).replace("\\n", "")
                param_dict = json.loads(temp)
                param_assign_value_list = ParamUtil.split_swagger_param_and_type(
                    param_dict, nontype=False
                )
                for param_item in param_assign_value_list:
                    for k, v in param_item.items():
                        new_k, new_v = self.splice_kv_str(k, v, kv_fix_list)
                        payload_assigin_str += (
                            self.CHAR_SPACE_8 + new_k + middle_char + new_v + "\n"
                        )
            else:
                print(f"api body type is error: {type(param_dict)}\n{param_dict}")
        return payload_assigin_str

    # put chars to k,v prefix and suffix.
    def splice_kv_str(self, k, v, kv_fix: list[str]) -> tuple[str, str]:
        k_prefix = kv_fix[0]
        k_suffix = kv_fix[1]
        v_prefix = kv_fix[2]
        v_suffix = kv_fix[3]
        new_k = k_prefix + str(k) + k_suffix
        new_v = v_prefix + str(v) + v_suffix
        return new_k, new_v


if __name__ == "__main__":
    a = GenerateCaseCode()
    # 接口信息
    api_yaml_file_path = (
        "merged.yaml"
    )
    # 生成的接口代码会保存到这个文件中
    case_file_path = "./case_template.py"
    rule_tool = NoneRule()
    a.produce_code_for_api_yaml(api_yaml_file_path, case_file_path, rule_tool)
