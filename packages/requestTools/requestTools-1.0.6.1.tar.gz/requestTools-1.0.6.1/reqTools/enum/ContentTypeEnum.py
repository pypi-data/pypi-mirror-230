import json
import logging
import urllib
from enum import Enum

log = logging.getLogger(__name__)

class ContentTypeEnum(Enum):
    """ContentType的格式枚举
    """
    FormUrlencoded = 'application/x-www-form-urlencoded'

    ApplicationJson = 'application/json'

    MultipartFormData = 'multipart/form-data'

    TextPlain = 'text/plain'

    ApplicationXml = 'application/xml'

    def __init__(self,contentType):
        self.contentType = contentType

    def parse(self,formData):

        if self == ContentTypeEnum.FormUrlencoded:
            return urllib.parse.urlencode(formData)

        elif self == ContentTypeEnum.ApplicationJson:
            return json.dumps(formData)

        elif self == ContentTypeEnum.TextPlain:
            text_plain = ""
            for key, value in formData.items():
                text_plain += f"{key}: {value}\n"
            return text_plain.strip()

        else :
            errorMsg = "Content-Type:" + self.contentType + ",form data processor not define!"
            raise ValueError(errorMsg)

    @staticmethod
    def getEnum(contentType):
        """
        根据枚举字符变量，找到对应枚举实例
        :param method: 枚举字符变量
        :return: 返回对应枚举实例
        """
        for name, contentTypeEnum in ContentTypeEnum.__members__.items():
            if contentTypeEnum.contentType == contentType:
                return contentTypeEnum