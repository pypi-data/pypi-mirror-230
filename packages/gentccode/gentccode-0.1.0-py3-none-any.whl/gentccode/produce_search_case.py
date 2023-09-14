import copy
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


def toc_server_search_cases(curl_file, test_case_file):
    o = {
        "filter": {
            "type": "binary_operator",
            "kind": "AND",
            "values": [
                {
                    "type": "atom",
                    "key": "ip_lan",
                    "method": "contains",
                    "value": "1.1.1.1",
                },
                {
                    "type": "atom",
                    "key": "resource_type",
                    "method": "equals",
                    "value": "physical",
                },
                {
                    "type": "atom",
                    "key": "az",
                    "method": "in",
                    "value": ["ap-my-1-private-c"],
                },
                {"type": "atom", "key": "id", "method": "equals", "value": "123"},
                {"type": "atom", "key": "state", "method": "in", "value": ["in_pool"]},
                {
                    "type": "atom",
                    "key": "segment",
                    "method": "in",
                    "value": ["ap-my-1-private-c: 978f15e4949dce5aaea1362c5b5cb9ee"],
                },
                {
                    "type": "atom",
                    "key": "service_tag",
                    "method": "in",
                    "value": ["vm-a"],
                },
                {
                    "type": "atom",
                    "key": "server_config",
                    "method": "contains",
                    "value": "dddd",
                },
                {"type": "atom", "key": "idc", "method": "in", "value": ["5SPD"]},
                {
                    "type": "atom",
                    "key": "platform",
                    "method": "in",
                    "value": ["Cache&KVc11111"],
                },
                {
                    "key": "tag",
                    "method": "in",
                    "type": "atom",
                    "value": "swp_ticket:234508",
                },
                {
                    "type": "atom",
                    "key": "ip_lan_list",
                    "method": "in",
                    "value": ["2.2.2.2"],
                },
                {
                    "type": "atom",
                    "key": "resource_node",
                    "method": "contains",
                    "value": "ai",
                },
                {
                    "type": "atom",
                    "key": "resource_node",
                    "method": "starts_with",
                    "value": "shopee.",
                },
            ],
        },
        "page_size": 10,
        "params": {"with_minimal_info": True},
    }
    aa = o["filter"]["values"]
    # 有二级结构的请求参数
    ip_lan_cases = {"ip_lan": ["contains", "in", "equals", "not_in"]}
    resource_type_cases = {"resource_type": ["in", "equals", "not_in"]}
    service_tag_cases = {"service_tag": ["contains", "in", "equals", "not_in"]}
    server_config_cases = {"server_config": ["contains", "equals", "not_in"]}
    platform_cases = {"platform": ["is_empty", "in", "is_not_empty", "not_in"]}
    ip_lan_list_cases = {"ip_lan_list": ["contains", "in", "equals", "not_in"]}
    param_cases = [
        ip_lan_cases,
        resource_type_cases,
        service_tag_cases,
        server_config_cases,
        platform_cases,
        ip_lan_list_cases,
    ]

    producted_cases = []
    for case in param_cases:
        for k, v in case.items():
            bb = copy.deepcopy(aa)
            for b in bb:
                if b["key"] == k:
                    for v2 in v:
                        b["method"] = v2
                        producted_cases.append(bb)

    ccp = CP()
    for case in producted_cases:
        ccp.product_param(case)
    res = ccp.get_unique_list()
    param_list = []
    for cp in res:
        for sub_param in cp:
            copy_o = copy.deepcopy(o)
            copy_o["filter"]["values"] = list(sub_param)
            param_list.append(copy_o)

    ptc.produce_case_by_curl(
        param_list=param_list,
        curl_file=curl_file,
        test_case_file=test_case_file,
        unique_char=True,
    )


def gen_case_for_dict_type_param(
    param: dict,
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


def replace_nested_key_value(d, keys, new_value):
    key_list = keys.split(".")
    current_key = key_list[0]

    if current_key in d:
        if len(key_list) == 2:
            d[current_key] = new_value
        else:
            replace_nested_key_value(d[current_key], ".".join(key_list[1:]), new_value)


if __name__ == "__main__":
    # read from curl
    curl_file = "./script/generated_result/curls.txt"
    case_file_path = "./script/generated_result/test_case_template.py"
    # toc_server_search_cases(curl_file=curl_file, test_case_file=case_file_path)
    o = {
        "page": 1,
        "page_size": 100,
        "with_segment_info": False,
        "filter": {
            "az_name_in": ["na-us-3-general-m"],
            "idc_name_in": ["AirTrunk B"],
            "az_type": "general",
            "region_key": "na-us-3",
            "az_location": "na-us-3",
        },
    }
    assert_response_str_after = 'assert len(response["data"]["azs"]) > 0'
    edit_payload_str_before = "request_model.body['filter'] = {}"
    gen_case_for_dict_type_param(
        param=o,
        node="filter.",
        curl_file=curl_file,
        test_case_file=case_file_path,
        assert_response_str_after=assert_response_str_after,
        edit_payload_str_before=edit_payload_str_before,
    )
