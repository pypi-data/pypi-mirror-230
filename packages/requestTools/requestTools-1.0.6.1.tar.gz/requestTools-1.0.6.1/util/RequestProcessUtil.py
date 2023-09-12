import json
import logging
import urllib.parse

from reqTools.enum.ContentTypeEnum import ContentTypeEnum
from reqTools.enum.MethodEnum import MethodEnum

log = logging.getLogger(__name__)

class RequestProcessUtil:

    @staticmethod
    def requestExecute(method,session,url,datas,headers,cookies):

        contentTypeEnum = ContentTypeEnum.getEnum(headers.get(("Content-Type"),
                                                  ContentTypeEnum.ApplicationJson.contentType))
        formData = contentTypeEnum.parse(datas)

        log.debug("Request URL:%s",url)
        log.debug("Request Method:%s",method)
        log.debug("Request headers:%s",str(headers))
        log.debug("Request cookies:%s",str(cookies))
        log.debug("form data:%s",formData)

        # get请求
        if method == MethodEnum.GET:
            response = session.get(url, data=formData, headers=headers, cookies=cookies)
        # post请求
        elif method == MethodEnum.POST:
            response = session.post(url, data=formData, headers=headers, cookies=cookies)
        # delete请求
        elif method == MethodEnum.DELETE:
            response = session.delete(url, data=formData, headers=headers, cookies=cookies)
        # 其他方式，默认post请求
        else :
            response = session.post(url, data=formData, headers=headers, cookies=cookies)

        return response