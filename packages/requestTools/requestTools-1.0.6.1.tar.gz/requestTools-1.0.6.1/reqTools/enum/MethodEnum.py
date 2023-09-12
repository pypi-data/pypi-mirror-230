from enum import Enum


class MethodEnum(Enum):
    """http请求方式枚举类
    """

    POST = 'POST'

    GET = 'GET'

    DELETE = 'DELETE'

    PUT = "PUT"

    HEAD = 'HEAD'

    OPTIONS = 'OPTIONS'

    PATCH = 'PATCH'

    TRACE = 'TRACE'

    CONNECT = 'CONNECT'

    def __init__(self,method):
        self.method = method

    @staticmethod
    def getEnum(method):
        """
        根据枚举字符变量，找到对应枚举实例
        :param method: 枚举字符变量
        :return: 返回对应枚举实例
        """
        for name, methodEnum in MethodEnum.__members__.items():
            if methodEnum.method == method:
                return methodEnum