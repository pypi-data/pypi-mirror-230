## 简介
gtc(generate test case) 是一个把http请求转换为测试代码的cli工具

## 功能

- [x] 支持解析curl命令
- [x] 支持解析postman文件
- [x] 支持解析swagger2文件
- [x] 支持解析curl文件并生成Jmeter性能脚本
- [x] 支持解析curl文件并生成Locust性能脚本
- [ ] 支持解析postman文件并生成Jmeter性能脚本
- [ ] 支持解析postman文件并生成Locust性能脚本
- [ ] 一键生成Jmeter性能压测方案脚本
## 用法
执行下面命令,会在当前目录生成api文件(`api.yaml`)和测试代码的脚本文件(`test_case.py`)
```bash
gtc -t curl curl.txt
gtc -t postman postman.json
gtc -t swagger2 swagger.json
gtc -t swagger2 swagger.json
----------------------------
gtc -t jmeter curl.txt
gtc -t locust curl.txt
```
## 已知问题

- 若postman文件中有变量,则不会生成相对应的代码块.