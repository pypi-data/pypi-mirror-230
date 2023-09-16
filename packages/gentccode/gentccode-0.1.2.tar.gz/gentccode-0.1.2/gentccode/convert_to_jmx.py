import json
import time
from urllib.parse import urlparse
from lxml import etree
from http_content_parser.generate_api_file import GenerateApiFile
from http_content_parser.req_data import ReqData
from gentccode.parse import ParseUtil


def jmeter_test_plan(root_xml):
    JmeterTestPlan = root_xml
    JmeterTestPlan.set("version", "1.2")
    JmeterTestPlan.set("properties", "5.0")
    JmeterTestPlan.set("jmeter", "5.6")
    return etree.SubElement(JmeterTestPlan, "hashTree")


def test_plan(parent_xml, plan_name):
    """

    :param parent_xml:
    :param plan_name:
    :return: etree object
    """
    testPlan = etree.SubElement(parent_xml, "TestPlan")
    testPlan.set("guiclass", "TestPlanGui")
    testPlan.set("testclass", "TestPlan")
    testPlan.set("testname", plan_name)
    testPlan.set("enabled", "true")
    stringProp = etree.SubElement(testPlan, "stringProp")
    stringProp.set("name", "TestPlan.comments")
    stringProp.text = ""
    boolProp1 = etree.SubElement(testPlan, "boolProp")
    boolProp1.set("name", "TestPlan.functional_mode")
    boolProp1.text = "false"
    boolProp2 = etree.SubElement(testPlan, "boolProp")
    boolProp2.set("name", "TestPlan.tearDown_on_shutdown")
    boolProp2.text = "false"
    boolProp3 = etree.SubElement(testPlan, "boolProp")
    boolProp3.set("name", "TestPlan.serialize_threadgroups")
    boolProp3.text = "true"
    elementProp = etree.SubElement(testPlan, "elementProp")
    elementProp.set("name", "TestPlan.user_defined_variables")
    elementProp.set("elementType", "Arguments")
    elementProp.set("guiclass", "ArgumentsPanel")
    elementProp.set("testclass", "Arguments")
    elementProp.set("testname", "User Defined Variables")
    elementProp.set("enabled", "true")
    collectionProp = etree.SubElement(elementProp, "collectionProp")
    collectionProp.set("name", "Arguments.arguments")
    stringProp2 = etree.SubElement(testPlan, "stringProp")
    stringProp2.set("name", "TestPlan.user_define_classpath")
    stringProp2.text = ""
    return etree.SubElement(parent_xml, "hashTree")


def thread_group(parent_xml):
    """

    :param parent_xml:
    :return: etree object
    """
    theadGroup = etree.SubElement(parent_xml, "ThreadGroup")
    theadGroup.set("guiclass", "ThreadGroupGui")
    theadGroup.set("testclass", "ThreadGroup")
    theadGroup.set("testname", "Thread Group")
    theadGroup.set("enabled", "true")
    stringProp = etree.SubElement(theadGroup, "stringProp")
    stringProp.set("name", "ThreadGroup.on_sample_error")
    stringProp.text = "continue"
    elementProp = etree.SubElement(theadGroup, "elementProp")
    set_kv_to_xml(
        elementProp,
        {
            "name": "ThreadGroup.main_controller",
            "elementType": "LoopController",
            "guiclass": "LoopControlPanel",
            "testclass": "LoopController",
            "testname": "Loop Controller",
            "enabled": "true",
        },
    )
    boolProp = etree.SubElement(elementProp, "boolProp")
    boolProp.set("name", "LoopController.continue_forever")
    boolProp.text = "false"
    stringProp = etree.SubElement(elementProp, "stringProp")
    stringProp.set("name", "LoopController.loops")
    stringProp.text = "1"
    stringProp = etree.SubElement(theadGroup, "stringProp")
    stringProp.set("name", "ThreadGroup.num_threads")
    stringProp.text = "1"
    stringProp = etree.SubElement(theadGroup, "stringProp")
    stringProp.set("name", "ThreadGroup.ramp_time")
    stringProp.text = "1"
    boolProp = etree.SubElement(theadGroup, "boolProp")
    boolProp.set("name", "ThreadGroup.scheduler")
    boolProp.text = "false"
    stringProp = etree.SubElement(theadGroup, "stringProp")
    stringProp.set("name", "ThreadGroup.duration")
    stringProp.text = ""
    stringProp = etree.SubElement(theadGroup, "stringProp")
    stringProp.set("name", "ThreadGroup.delay")
    stringProp.text = ""
    return etree.SubElement(parent_xml, "hashTree")


def arguments(parent_xml):
    """

    :param parent_xml:
    :return: etree object
    """
    Arguments = etree.SubElement(parent_xml, "ThreadGroup")
    Arguments.set("guiclass", "ArgumentsPanel")
    Arguments.set("testclass", "Arguments")
    Arguments.set("testname", "User defined variables")
    Arguments.set("enabled", "true")
    collectionProp = etree.SubElement(Arguments, "collectionProp")
    collectionProp.set("name", "Arguments.arguments")
    return etree.SubElement(parent_xml, "hashTree")


def header_manager(parent_xml, headers: dict):
    HeaderManager = etree.SubElement(parent_xml, "HeaderManager")
    set_kv_to_xml(
        HeaderManager,
        {
            "guiclass": "HeaderPanel",
            "testclass": "HeaderManager",
            "testname": "HTTP Header Manager",
        },
    )
    collectionProp = etree.SubElement(HeaderManager, "collectionProp")
    collectionProp.set("name", "HeaderManager.headers")
    if headers:
        for k, v in headers.items():
            elementProp = etree.SubElement(collectionProp, "elementProp")
            elementProp.set("name", "")
            elementProp.set("elementType", "Header")

            stringProp = etree.SubElement(elementProp, "stringProp")
            stringProp.set("name", "Header.name")
            stringProp.text = k

            stringProp = etree.SubElement(elementProp, "stringProp")
            stringProp.set("name", "Header.value")
            stringProp.text = str(v)

    return etree.SubElement(parent_xml, "hashTree")


def response_assertion(parent_xml):
    responseAssertion = etree.SubElement(parent_xml, "ResponseAssertion")
    set_kv_to_xml(
        responseAssertion,
        {
            "guiclass": "AssertionGui",
            "testclass": "ResponseAssertion",
            "testname": "Response Assertion",
        },
    )
    collectionProp = etree.SubElement(responseAssertion, "collectionProp")
    collectionProp.set("name", "Asserion.test_strings")
    stringProp = etree.SubElement(responseAssertion, "stringProp")
    stringProp.set("name", "Assertion.custom_message")
    stringProp.text = ""  # 这个属性必须要有值,空值也得加上
    stringProp = etree.SubElement(responseAssertion, "stringProp")
    stringProp.set("name", "Assertion.test_field")
    stringProp.text = "Assertion.response_data"
    boolProp = etree.SubElement(responseAssertion, "boolProp")
    boolProp.set("name", "Assertion.assume_success")
    boolProp.text = "false"
    intProp = etree.SubElement(responseAssertion, "intProp")
    intProp.set("name", "Assertion.test_type")
    intProp.text = "16"
    return etree.SubElement(parent_xml, "hashTree")


def json_path_assertion(parent_xml):
    jsonAssertion = etree.SubElement(parent_xml, "JSONPathAssertion")
    set_kv_to_xml(
        jsonAssertion,
        {
            "guiclass": "JSONPathAssertionGui",
            "testclass": "JSONPathAssertion",
            "testname": "JSON Assertion",
        },
    )
    stringProp = etree.SubElement(jsonAssertion, "stringProp")
    stringProp.set("name", "JSON_PATH")
    stringProp.text = "$.error"
    stringProp = etree.SubElement(jsonAssertion, "stringProp")
    stringProp.set("name", "EXPECTED_VALUE")
    stringProp.text = "0"
    boolProp = etree.SubElement(jsonAssertion, "boolProp")
    boolProp.set("name", "JSONVALIDATION")
    boolProp.text = "false"
    boolProp = etree.SubElement(jsonAssertion, "boolProp")
    boolProp.set("name", "EXPECT_NULL")
    boolProp.text = "false"
    boolProp = etree.SubElement(jsonAssertion, "boolProp")
    boolProp.set("name", "INVERT")
    boolProp.text = "false"
    boolProp = etree.SubElement(jsonAssertion, "boolProp")
    boolProp.set("name", "ISREGEX")
    boolProp.text = "true"
    return etree.SubElement(parent_xml, "hashTree")


def http_sampler_proxy(parent_xml, payload: dict):
    # sample list
    HTTPSamplerProxy = etree.SubElement(parent_xml, "HTTPSamplerProxy")
    set_kv_to_xml(
        HTTPSamplerProxy,
        {
            "guiclass": "HttpTestSampleGui",
            "testclass": "HTTPSamplerProxy",
            "testname": payload.get("sampler_comments")
            + "-"
            + str(payload.get("path")).replace("//", "/"),
            "enabled": "true",
        },
    )
    # parameter
    if payload.get("params_type") == "parameters":
        elementProp = etree.SubElement(HTTPSamplerProxy, "elementProp")
        set_kv_to_xml(
            elementProp,
            {
                "name": "HTTPsampler.Arguments",
                "elementType": "Arguments",
                "guiclass": "HTTPArgumentsPanel",
                "testclass": "Arguments",
                "testname": "User Defined Variables",
            },
        )
        collectionProp = etree.SubElement(elementProp, "collectionProp")
        collectionProp.set("name", "Arguments.arguments")
        if payload.get("params"):
            params = payload.get("params")
            # params = json.loads(params)
            for k, v in params.items():
                elementProp = etree.SubElement(collectionProp, "elementProp")
                set_kv_to_xml(
                    elementProp,
                    {
                        "name": "",
                        "elementType": "HTTPArgument",
                    },
                )
                stringProp = etree.SubElement(elementProp, "stringProp")
                stringProp.set("name", "Argument.metadata")
                stringProp.text = "="

                boolProp = etree.SubElement(elementProp, "boolProp")
                boolProp.set("name", "HTTPArgument.use_equals")
                boolProp.text = "true"

                stringProp = etree.SubElement(elementProp, "stringProp")
                stringProp.set("name", "Argument.name")
                stringProp.text = k

                stringProp = etree.SubElement(elementProp, "stringProp")
                stringProp.set("name", "Argument.value")
                stringProp.text = str(v)

    # postBodyRaw
    elif payload.get("params_type") == "body_data":
        boolProp = etree.SubElement(HTTPSamplerProxy, "boolProp")
        boolProp.set("name", "HTTPSampler.postBodyRaw")
        boolProp.text = "true"
        elementProp = etree.SubElement(HTTPSamplerProxy, "elementProp")
        set_kv_to_xml(
            elementProp,
            {"name": "HTTPsampler.Arguments", "elementType": "Arguments"},
        )
        collectionProp = etree.SubElement(elementProp, "collectionProp")
        collectionProp.set("name", "Arguments.arguments")

        elementProp = etree.SubElement(collectionProp, "elementProp")
        elementProp.set("name", "")
        elementProp.set("elementType", "HTTPArgument")

        boolProp = etree.SubElement(elementProp, "boolProp")
        boolProp.set("name", "HTTPArgument.always_encode")
        boolProp.text = "false"
        # body_data
        stringProp = etree.SubElement(elementProp, "stringProp")
        stringProp.set("name", "Argument.value")
        stringProp.text = json.dumps(payload.get("params"))

        stringProp = etree.SubElement(elementProp, "stringProp")
        stringProp.set("name", "Argument.metadata")
        stringProp.text = "="
    else:
        raise Exception("params_type is error")
    # host
    stringProp = etree.SubElement(HTTPSamplerProxy, "stringProp")
    stringProp.set("name", "HTTPSampler.domain")
    stringProp.text = payload.get("host")

    # port
    stringProp = etree.SubElement(HTTPSamplerProxy, "stringProp")
    stringProp.set("name", "HTTPSampler.port")
    stringProp.text = payload.get("port")

    # protocol
    stringProp = etree.SubElement(HTTPSamplerProxy, "stringProp")
    stringProp.set("name", "HTTPSampler.protocol")
    stringProp.text = payload.get("http_type", "http")

    # encoding
    stringProp = etree.SubElement(HTTPSamplerProxy, "stringProp")
    stringProp.set("name", "HTTPSampler.contentEncoding")
    stringProp.text = "UTF-8"

    # path
    stringProp = etree.SubElement(HTTPSamplerProxy, "stringProp")
    stringProp.set("name", "HTTPSampler.path")
    stringProp.text = str(payload.get("path")).replace("//", "/").replace("/{", "/${")

    # method
    stringProp = etree.SubElement(HTTPSamplerProxy, "stringProp")
    stringProp.set("name", "HTTPSampler.method")
    stringProp.text = payload.get("method").upper()

    # follow redirects
    boolProp = etree.SubElement(HTTPSamplerProxy, "boolProp")
    boolProp.set("name", "HTTPSampler.follow_redirects")
    boolProp.text = "true"

    # use keepalive
    boolProp = etree.SubElement(HTTPSamplerProxy, "boolProp")
    boolProp.set("name", "HTTPSampler.use_keepalive")
    boolProp.text = "true"

    # embedded url re
    stringProp = etree.SubElement(HTTPSamplerProxy, "stringProp")
    stringProp.set("name", "HTTPSampler.embedded_url_re")
    stringProp.text = ""

    # connect timeout
    stringProp = etree.SubElement(HTTPSamplerProxy, "stringProp")
    stringProp.set("name", "HTTPSampler.connect_timeout")
    stringProp.text = ""

    # response timeout
    stringProp = etree.SubElement(HTTPSamplerProxy, "stringProp")
    stringProp.set("name", "HTTPSampler.response_timeout")
    stringProp.text = ""

    # comments
    stringProp = etree.SubElement(HTTPSamplerProxy, "stringProp")
    stringProp.set("name", "TestPlan.comments")
    stringProp.text = payload.get("sampler_comments")


def controller(parent_xml, payloads: list):
    for payload in payloads:
        GenericController = etree.SubElement(parent_xml, "GenericController")
        GenericController.set("guiclass", "LogicControllerGui")
        GenericController.set("testclass", "GenericController")
        GenericController.set("testname", payload.get("controller_name"))
        GenericController.set("enabled", "true")
        stringProp = etree.SubElement(GenericController, "stringProp")
        stringProp.set("name", "TestPlan.comments")
        stringProp.text = payload.get("description")
        shashTree = etree.SubElement(parent_xml, "hashTree")
        header_manager(shashTree, headers=payload["header"])
        # http sampler
        http_sampler_proxy(shashTree, payload)
        # http response assert, hasTree 必须要当前树下,不能做为参数传下去
        responseAssertionTree = etree.SubElement(shashTree, "hashTree")
        json_path_assertion(responseAssertionTree)


def set_kv_to_xml(obj_xml, datas):
    """

    :param obj_xml:
    :param datas:
    :return:
    """
    for key, value in datas.items():
        obj_xml.set(key, value)


def write_to_jmx(payloads: list):
    jmeterTestPlan = etree.Element("jmeterTestPlan")
    hashTree = jmeter_test_plan(jmeterTestPlan)
    testPlan = test_plan(hashTree, "autotest")
    threadGroup = thread_group(testPlan)
    controller(threadGroup, payloads)
    etree.tostring(jmeterTestPlan, pretty_print=True)
    tree = etree.ElementTree(jmeterTestPlan)
    now_date = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
    tree.write(
        f"jmeter-{now_date}.jmx",
        pretty_print=True,
        xml_declaration=True,
        encoding="utf-8",
    )


def _get_param_by_method(payload: ReqData):
    if payload.method == "get":
        return payload.query_param
    else:
        return payload.body


def _get_param_type_by_method(method):
    if method == "get":
        return "parameters"
    else:
        return "body_data"


def _split_url(url):
    if url:
        parsed = urlparse(url)
        # 输出：https, www.example.com
        l = (parsed.netloc).split(":")
        port = ""
        if len(l) > 1:
            port = l[1]
        return parsed.scheme, l[0], port
    else:
        return "", "", ""


def _reduce_url_path(path):
    if path[0] != "/":
        return "/" + path
    else:
        return path


def convert_payloads_of_yaml_to_jmx_file(file_path):
    api_infos = ParseUtil.parse_api_info_from_yaml(file_path)
    payload_list = [r for _, r in api_infos.items()]
    jmx_payloads = convert_payloads_to_jmx_model(payload_list)
    write_to_jmx(payloads=jmx_payloads)


def convert_payloads_of_curl_to_jmx_file(curl_file_path):
    gaf = GenerateApiFile()
    http_payloads = gaf.convert_curl_data_to_model(curl_file_path)
    jmx_payloads = convert_payloads_to_jmx_model(http_payloads=http_payloads)
    write_to_jmx(payloads=jmx_payloads)


def convert_payloads_to_jmx_model(http_payloads: list[ReqData]) -> list:
    i = 1
    jmx_payloads = []
    for http_payload in http_payloads:
        http_payload = parse_req_data_model(http_payload)
        p = {}
        temp_url = http_payload.original_url
        url_split = _split_url(temp_url)
        p["http_type"] = url_split[0]
        p["host"] = url_split[1]
        p["port"] = url_split[2]
        p["path"] = _reduce_url_path(http_payload.path)
        p["method"] = http_payload.method
        p["header"] = http_payload.header
        p["params"] = _get_param_by_method(http_payload)
        p["params_type"] = _get_param_type_by_method(http_payload.method)
        p["sampler_comments"] = str(i) + "-"
        p["controller_name"] = "controller" + str(i)
        i += 1
        jmx_payloads.append(p)
    return jmx_payloads


def parse_req_data_model(req: ReqData):
    if isinstance(req.header, str):
        req.header = json.loads(req.header)
    if isinstance(req.body, str):
        req.body = json.loads(req.body)
    if isinstance(req.query_param, str):
        req.query_param = json.loads(req.query_param)
    return req


if __name__ == "__main__":
    p1 = {
        "host": "www.baidu.com",
        "port": "443",
        "path": "/api/v3",
        "method": "post",
        "header": '{"h1":2}',
        "params": "",
        "http_type": "https",
        "params_type": "parameters",
        "sampler_comments": "test-comments",
        "controller_name": "test-controller",
    }
    yaml_file_path = "./script/generated_result/api_template.yaml"
    curl_file = "./script/generated_result/curls.txt"
    convert_payloads_of_curl_to_jmx_file(curl_file_path=curl_file)
