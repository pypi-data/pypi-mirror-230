from abc import ABC, abstractmethod
import yaml


class BaseRule(ABC):

    @abstractmethod
    def get_api_mysql_method(self, api_name):
        pass


class NoneRule(BaseRule):
    def get_api_mysql_method(self, api_name):
        return {}


class SwaggerRule(BaseRule):
    def __init__(self) -> None:
        with open('./script/swagger_rule.yaml', 'r') as f:
            rule_dict = yaml.safe_load(f)
        self.rule_dict = rule_dict

    def get_api_mysql_method(self, api_name):
        return self.rule_dict.get(api_name)


if __name__ == '__main__':
    rule = SwaggerRule()
    api_name = 'api_v2_server_az_create-segment_post'
    v = rule.get_api_mysql_method(api_name=api_name)
    print(v)
    rule2 = NoneRule()
    v3 = rule2.get_api_mysql_method(api_name)
    print(v3)
