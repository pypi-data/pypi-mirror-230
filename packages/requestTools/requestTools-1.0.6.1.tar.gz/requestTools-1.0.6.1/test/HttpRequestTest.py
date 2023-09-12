import logging
import unittest

from reqTools.HttpRequestProcessor import NormalHttpRequestProcessor
from reqTools.enum.MethodEnum import MethodEnum


# 配置日志输出的格式
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(name)s - %(message)s', level=logging.DEBUG)

class XXXNormalHttpRequestProcessor(NormalHttpRequestProcessor):
    """一个基本的http请求处理实现类
    该类重新实现了setCookieFileName,setUrl,setMethod,setFormValues5个抽象方法
    """
    # 设置cookie文件名称
    def setCookieFileName(self):
        return "test.txt"

    # 设置Url
    def setUrl(self, dynamicParams=None):
        return "https://www.jianshu.com/shakespeare/notes/112395709/user_notes"

    # 设置方法
    def setMethod(self):
        return MethodEnum.GET

    # 设置表单信息
    def setStaticFormValues(self):
        # 固定不变的请求参数
        formValues = {}
        return formValues

class HttpRequestTest(unittest.TestCase):

    def test_GetRespnse(self):
        xxxNormalHttpRequestProcessor = XXXNormalHttpRequestProcessor()
        responseDataJson = xxxNormalHttpRequestProcessor.getResponse()

        self.assertIsNotNone(responseDataJson)

unittest.main()