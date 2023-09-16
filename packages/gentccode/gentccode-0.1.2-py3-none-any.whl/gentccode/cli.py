import os
import click
from gentccode.convert_to_jmx import convert_payloads_of_curl_to_jmx_file
from gentccode.convert_to_locust import product_locust_script
from gentccode.produce_search_case import gen_cp_test_case
from gentccode.produce_test_case import ProduceTestCase


ptc = ProduceTestCase()
# 生成的接口信息会保存到这个文件中
api_yaml_file_path = "api.yaml"
# 生成的接口代码会保存到这个文件中
case_file_path = "test_cases.py"


@click.group()
def cli1():
    pass


@cli1.command(help="generate test code by http's payload")
@click.option("-n", "--node", required=True, help="json node, like: '.','a.','a.b.'")
@click.argument("filename", type=click.Path(exists=True))
def cp(node, filename):
    gen_cp_test_case(
        node=node,
        curl_file=filename,
    )


@click.group()
def cli2():
    pass


@cli2.command(help="generate test code by curl file")
@click.argument("filename", type=click.Path(exists=True))
def curl(filename):
    ptc.produce_case_by_yaml_for_curl(filename, api_yaml_file_path, case_file_path)


@click.group()
def cli3():
    pass


@cli3.command(help="generate test code by swagger json file")
@click.argument("filename", type=click.Path(exists=True))
def swagger2(filename):
    ptc.produce_case_by_yaml_for_swagger2(filename, api_yaml_file_path, case_file_path)


@click.group()
def cli4():
    pass


@cli4.command(help="auto generate openapi document's test code")
@click.argument("filename", type=click.Path(exists=True))
def openapi(filename):
    ptc.produce_merged_case_for_openapi_and_curl(curl_file_path=filename)


@click.group()
def cli5():
    pass


@cli5.command(help="generate locust script by curl file")
@click.argument("filename", type=click.Path(exists=True))
def locust(filename):
    product_locust_script(yaml_file_path=filename)


@click.group()
def cli6():
    pass


@cli6.command(help="generate jmeter script by curl file")
@click.argument("filename", type=click.Path(exists=True))
def jmeter(filename):
    convert_payloads_of_curl_to_jmx_file(curl_file_path=filename)


@click.group()
def cli7():
    pass


@cli7.command(help="auto generate swagger2 document's test code")
@click.argument("filename", type=click.Path(exists=True))
def swagger_at(filename):
    ptc.produce_merged_case_for_swagger_and_curl(curl_file_path=filename)


cli = click.CommandCollection(sources=[cli1, cli2, cli3, cli4, cli5, cli6, cli7])


def main():
    if os.path.exists(api_yaml_file_path):
        with open(api_yaml_file_path, "w") as f:
            f.write("")  # 先清空之前的内容
    cli()
