import unittest
import os
from generate import generate_config

# 构建参数
request_data = {
    'publicAppId': 'WebApi',  # 公共应用appid
    'appId': 'TestAPI'  # 当前应用id
}
config_result = 'config_result.txt'
configTemplates = [[config_result, './test/config_template.txt']]


class TestGenerate(unittest.TestCase):

    def test_generate(self):
        config_result_path = "./%s" % config_result
        try:
            generate_config.generate('apollo', 'DEV', '', False,
                                     False, '', '', configTemplates, request_data)
            file_object = open(config_result_path, encoding='utf-8')
            all_the_text = file_object.read()  # 结果为str类型
            print(all_the_text)
            file_object.close()
            self.assertEqual(all_the_text, '我是"Development"环境')
        finally:
            os.remove(config_result_path)


if __name__ == '__main__':
    unittest.main()
