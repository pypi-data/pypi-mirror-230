import re
import time
from http_content_parser.req_data import ReqData
from gentccode.parse import ParseUtil

CHAR_SPACE_8 = "        "
CHAR_SPACE_4 = "    "


def get_import_str():
    import_str = (
        "from locust import HttpUser, task, between\n"
        + "class QuickstartUser(HttpUser):\n"
        + f"{CHAR_SPACE_4}wait_time = between(1, 5)\n\n"
    )
    return import_str


def get_method1_str():
    on_start_str = f"{CHAR_SPACE_4}def on_start(self):\n" + f"{CHAR_SPACE_8}pass\n\n"

    return on_start_str


def get_method_task_str(payload: ReqData):
    method = payload.method
    host = payload.host
    path = payload.path
    query_param = payload.query_param
    if query_param:
        s = f'"{host}{path}{query_param}"'
    else:
        s = f'"{host}{path}"'
    if method != "get":
        var_str = f"{CHAR_SPACE_8}body_json={payload.body}\n"
        s += f", json=body_json"
    else:
        var_str = ""

    method_name = replace_api_label_chars(path)
    task_str = (
        f"{CHAR_SPACE_4}@task\n"
        + f"{CHAR_SPACE_4}def {method_name}(self):\n"
        + var_str
        + f"{CHAR_SPACE_8}self.client.{method}({ s })\n\n"
    )
    return task_str


def replace_api_label_chars(string):
    pattern = r"[-+@?={}/.]"  # 定义要匹配的特殊字符模式
    replacement = "_"  # 替换为的字符串

    new_string = re.sub(pattern, replacement, string)
    return new_string


def product_locust_script(yaml_file_path):
    now_date = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
    py_name = f"locust-{now_date}.py"
    with open(py_name, "at") as f:
        f.write(get_import_str() + get_method1_str())
        api_infos = ParseUtil.parse_api_info_from_yaml(yaml_file_path)
        for k, _ in api_infos.items():
            py_str = get_method_task_str(api_infos[k])
            f.write(py_str)


if __name__ == "__main__":
    with open("aa.py", "at") as f:
        f.write(get_import_str() + get_method1_str())
        yaml_file_path = "merged.yaml"
        api_infos = ParseUtil.parse_api_info_from_yaml(yaml_file_path)
        for k, _ in api_infos.items():
            py_str = get_method_task_str(api_infos[k])
            f.write(py_str)
