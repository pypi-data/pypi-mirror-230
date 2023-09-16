import copy
import json
from gentccode.cartesian_for_case import CP
from gentccode.produce_test_case import ProduceTestCase


ptc = ProduceTestCase()


def remove_items(o_dict: dict, keep_items: list[str]):
    copy_dict = {}
    for k, v in o_dict.items():
        for ki in keep_items:
            if ki == k:
                copy_dict[ki] = v
    return copy_dict


def gen_case_for_dict_type_param(
    node: str,
    curl_file: str,
    test_case_file: str,
    **kwargs,
):
    """把请求参数以笛卡尔积的方式生成测试用例代码

    Args:
        param (dict): 请求参数 {'a':{'b':2}}
        node (str): 参数所在的层级, 比如`.` or `a.` or `a.b.`
        curl_file (str): 接口的抓包数据
        test_case_file (str): 生成的代码的文件路径
    """
    param = ptc.get_request_payload(curl_file=curl_file)[0]
    if isinstance(param, str):
        param = json.loads(param)
    sub_param = {}
    has_nest = False
    if node == ".":
        sub_param = param
    else:
        o = copy.deepcopy(param)
        for k in node.split("."):
            if k:
                sub_param = o.get(k)
                if isinstance(sub_param, dict):
                    o = sub_param
        has_nest = True

    ccp = CP()
    ccp.product_param(sub_param)
    unique_case = ccp.get_unique_list()
    param_list = []
    for case in unique_case:
        for c in case:
            copy_param = copy.deepcopy(param)
            new_d = remove_items(sub_param, list(c))
            if has_nest:
                replace_nested_key_value(copy_param, node, new_d)
                param_list.append(copy_param)
            else:
                param_list.append(new_d)
    ptc.produce_case_by_curl(
        param_list=param_list,
        curl_file=curl_file,
        test_case_file=test_case_file,
        unique_char=True,
        **kwargs,
    )


def gen_cp_test_case(node, curl_file, **kwargs):
    gen_case_for_dict_type_param(
        node,
        curl_file,
        test_case_file="test_case.py",
        **kwargs,
    )


def replace_nested_key_value(d, keys, new_value):
    key_list = keys.split(".")
    current_key = key_list[0]

    if current_key in d:
        if len(key_list) == 2:
            d[current_key] = new_value
        else:
            replace_nested_key_value(d[current_key], ".".join(key_list[1:]), new_value)


if __name__ == "__main__":
    curl_file = "curls.txt"
    case_file_path = "test_case.py"
    assert_response_str_after = 'assert len(response["data"]["azs"]) > 0'
    edit_payload_str_before = "request_model.body['filter'] = {}"
    gen_case_for_dict_type_param(
        node="filter.",
        curl_file=curl_file,
        test_case_file=case_file_path,
        assert_response_str_after=assert_response_str_after,
        edit_payload_str_before=edit_payload_str_before,
    )
