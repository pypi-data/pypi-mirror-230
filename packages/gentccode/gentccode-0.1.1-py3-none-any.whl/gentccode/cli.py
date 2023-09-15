import click
from gentccode.convert_to_jmx import convert_payloads_of_curl_to_jmx_file
from gentccode.convert_to_locust import product_locust_script
from gentccode.produce_test_case import ProduceTestCase


@click.command()
@click.option(
    "-t",
    "--file_type",
    required=True,
    type=click.Choice(
        ["curl", "postman", "swagger2", "jmeter", "locust"], case_sensitive=False
    ),
)
@click.argument("filename", type=click.Path(exists=True))
def gen_code(file_type, filename):
    ptc = ProduceTestCase()
    # 生成的接口信息会保存到这个文件中
    api_yaml_file_path = "api.yaml"
    # 生成的接口代码会保存到这个文件中
    case_file_path = "test_cases.py"
    with open(api_yaml_file_path, "w") as f:
        f.write("")  # 先清空之前的内容
    if file_type == "curl":
        ptc.produce_case_by_yaml_for_curl(filename, api_yaml_file_path, case_file_path)
    elif file_type == "swagger2":
        ptc.produce_case_by_yaml_for_swagger2(
            filename, api_yaml_file_path, case_file_path
        )
    elif file_type == "postman":
        ptc.produce_case_by_yaml_for_postman(
            filename, api_yaml_file_path, case_file_path
        )
    elif file_type == "swagger_at":
        ptc.produce_merged_case_for_swagger_and_curl(curl_file_path=filename)
    elif file_type == "openapi_at":
        ptc.produce_merged_case_for_openapi_and_curl(curl_file_path=filename)
    elif file_type == "jmeter":
        convert_payloads_of_curl_to_jmx_file(curl_file_path=filename)
    elif file_type == "locust":
        product_locust_script(yaml_file_path=filename)


# if __name__ == "__main__":
def main():
    gen_code()
