import json
from abc import ABC, abstractmethod

import requests
import logging

from util.FileUtil import FileUtil
from util.RequestParamsUtil import RequestParamsUtil
from util.RequestProcessUtil import RequestProcessUtil

log = logging.getLogger(__name__)


class NormalHttpRequestProcessor(ABC):
    """常用的数据处理基类，适用于执行一次psot/get请求后，并且返回执行结果json对象

    该类是一个抽象的基类，使用时，需要实现一个子类来继承该基类，并在子类中，重新实现setCookieFileName、setUrl、setMethod、setFormValues
    5个抽象方法。

    """

    @abstractmethod
    def setCookieFileName(self):
        """
        设置cookie文件的名称，这是个抽象方法，子类需要重新实现
        :return:
        """
        pass

    @abstractmethod
    def setUrl(self, dynamicParams=None):
        """
        设置请求URL地址，这是个抽象方法，子类需要重新实现

        :param dynamicParams: key-value形式数据字典

        :return:
        """
        pass

    @abstractmethod
    def setMethod(self):
        """
        设置请求提交方式，post or get等请求，具体参见 MethodEnum 枚举实现，这是个抽象方法，子类需要重新实现

        :return: MethodEnum枚举类实例
        """
        pass

    @abstractmethod
    def setStaticFormValues(self):
        """
        设置固定不变的请求数据

        :return: 返回要提交的请求数据
        """

        pass

    def getCookieFile(self):
        """
        :return: 返回cookie file文件完整路径

        """
        return FileUtil.getProjectRootPath()+'/cookiefile/'+self.setCookieFileName()

    def getHeaders(self):
        """
        从cookieFileName中解析headers请求对象体
        :return: 返回headers
        """
        return RequestParamsUtil.getHeadersFromFile(self.getCookieFile())

    def getCookies(self):
        """
        从cookieFileName中解析cookies请求对象体
        :return: 返回cookies
        """
        return RequestParamsUtil.getCookiesFromFile(self.getCookieFile())

    def getUrl(self, dynamicParams=None):
        """
        :param dynamicParams: key-value形式数据字典

        :return: 返回请求url地址
        """
        return self.setUrl(dynamicParams)

    def getMethod(self):
        """
        :return: 返回请求方式，post or get
        """
        return self.setMethod()

    def getFormValues(self, dynamicParams=None):
        """
        返回要提交的请求数据

        :param dynamicParams: key-value形式数据字典
        :return: 返回要提交的请求数据
        """

        formValues = self.setStaticFormValues() if self.setStaticFormValues() is not None else {};

        # 合并动态的请求参数
        if dynamicParams is not None:
            formValues = {**formValues, **dynamicParams}

        return formValues

    def getResponse(self, dynamicParams=None):
        """
        提交请求，并且返回请求执行结果

        :param dynamicParams: key-value形式数据字典，默认为None

        :return: 返回请求执行结果json对象
        """
        session = requests.session()

        try:
            method = self.getMethod()
            datas = self.getFormValues(dynamicParams)
            url = self.getUrl()
            response = RequestProcessUtil.requestExecute(method, session, url, datas, self.getHeaders(), self.getCookies())

            log.debug("reponse text:%s" , response.text)

            return json.loads(response.text)

        finally:
            session.close()


class PageDataHttpRequestProcessor(NormalHttpRequestProcessor):
    """ 获取所有分页数据请求执行器基类

    该类是一个抽象的基类，继承NormalHttpRequestProcessor，使用时，需要重新定义一个子类来继承该基类，并在子类中，
    根据需要实现setCookieFileName、setUrl、setMethod、setFormValues、getTotal、getCurrentPageDatas、parseRowValues、setCurrentPageNumberKey 9个基类方法。

    """

    CURRENT_PAGE_NUMBER = "currentPageNumber"

    @abstractmethod
    def getTotal(self,pageJsonObj):
        """
        从当前页请求Json数据对象中解析出分页数据的总条数

        :param pageJsonObj: 当前页请求Json数据对象

        :return: 数据总条数
        """
        pass

    @abstractmethod
    def getCurrentPageDatas(self, pageJsonObj):
        """
        从当前页请求Json数据对象中解析出页面数据

        :param pageJsonObj: 当前页请求Json数据对象

        :return: 当前页数据Json对象
        """
        pass

    @abstractmethod
    def setCurrentPageNumberKey(self):
        """
        分页请求的页码属性名，例如：currentPage、pageNumber等属性名

        :return: 提交请求的页码属性key
        """
        pass

    @abstractmethod
    def parseRowValues(self, rowJsonObj):
        """
        按行解析出需要使用的每一行数据

        :param rowJsonObj: 行数据Json对象

        :return: 按需返回需要使用的行数据
        """
        pass

    def getFormValues(self, dynamicParams=None):
        """
        返回要提交的请求数据

        :param dynamicParams: key-value形式数据字典
        :return: 返回要提交的请求数据
        """

        formValues = super().getFormValues()

        # 内部设置当前页请求参数
        if self.setCurrentPageNumberKey() is not None:
            formValues[self.setCurrentPageNumberKey()] = dynamicParams[self.CURRENT_PAGE_NUMBER]

        return formValues

    def getResponse(self, dynamicParams=None):
        """
        提交请求，并且返回请求执行结果

        :param dynamicParams: key-value形式数据字典，默认为None

        :return: 返回所有行数据列表
        """

        session = requests.session()
        dynamicParams = {} if dynamicParams is None else dynamicParams

        try:
            allDatas = []
            pageNmuber = 1
            method = self.setMethod()

            while (1):
                dynamicParams[self.CURRENT_PAGE_NUMBER] = pageNmuber

                datas = self.getFormValues(dynamicParams)
                url = self.getUrl(dynamicParams)

                response = RequestProcessUtil.requestExecute(method, session, url, datas, self.getHeaders(),
                                                             self.getCookies())
                log.debug("reponse text:%s",response.text)

                jsonObj = json.loads(response.text)
                if (len(allDatas) >= self.getTotal(pageJsonObj=jsonObj)):
                    break

                rows = self.getCurrentPageDatas(jsonObj)
                for index, row in enumerate(rows):
                    rowDict = self.parseRowValues(rowJsonObj=row)
                    log.debug("rowDict:%s", str(rowDict))
                    allDatas.append(rowDict)

                pageNmuber = pageNmuber + 1

            return allDatas

        finally:
            session.close()