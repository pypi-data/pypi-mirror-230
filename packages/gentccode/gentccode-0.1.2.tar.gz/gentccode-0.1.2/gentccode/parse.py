from typing import Dict
import yaml
import json
import logging
from http_content_parser.req_data import ReqData


class ParseUtil(object):
    @staticmethod
    def parse_api_info_from_yaml(yaml_file_path: str) -> Dict[str, ReqData]:
        cases = {}
        """读取yaml格式的http请求数据"""
        with open(yaml_file_path, "rt") as f:
            try:
                cases = yaml.safe_load(f.read())
            except Exception as ex:
                logging.error("read yaml error: " + yaml_file_path)
                raise ex

        result = {}
        # 封装yaml中的数据到reqData中
        for key in cases.keys():
            req_data = ReqData()
            req_data.path = cases[key]["path"]
            if not req_data.path:
                logging.exception("the url path is null in yaml file")
            req_data.method = cases[key]["method"]
            if not req_data.method:
                logging.exception("the method is null in yaml file")
            # body,header,params必须为dict类型
            body_type = type(cases[key]["body"])
            header_type = type(cases[key]["header"])
            params_type = type(cases[key]["query_param"])
            if cases[key].get("path_param"):
                path_param = cases[key]["path_param"]
                if isinstance(path_param, str):
                    req_data.path_param = json.loads(path_param)
                else:
                    req_data.path_param = path_param
            if body_type == str:
                req_data.body = json.loads(cases[key]["body"])
            else:
                req_data.body = cases[key]["body"]
            if header_type == str:
                req_data.header = json.loads(cases[key]["header"])
            else:
                req_data.header = cases[key]["header"]
            # only when request method is get, there will include params filed
            if cases[key]["method"] == "get":
                if params_type == str:
                    req_data.query_param = json.loads(cases[key]["query_param"])
                else:
                    req_data.query_param = cases[key]["query_param"]
            req_data.original_url = cases[key]["original_url"]
            result[key] = req_data

        return result
