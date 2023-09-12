import logging

log = logging.getLogger(__name__)

class RequestParamsUtil:

    @staticmethod
    def getCookies(cookiesStr):
        cookies = {}
        for cookie in cookiesStr.split("; "):
            cookieKeyValue = cookie.split("=")
            cookies[cookieKeyValue[0]] = cookieKeyValue[1]

        return cookies

    @staticmethod
    def getHeaders():
        headers = {
            "accept": "application/json, text/plain, */*",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "sec-ch-ua": "\"Google Chrome\";v=\"87\", \" Not;A Brand\";v=\"99\", \"Chromium\";v=\"87\"",
            "sec-ch-ua-mobile": "?0",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
            "x-xsrf-token": "3f492c8c-81b4-478d-9c21-9c7e7fa59d23"
        }
        return headers

    @staticmethod
    def getCookiesFromFile(file):
        cookies = {}
        fileObj = open(file,"r")
        try:
            for line in fileObj.readlines():
                line = line.strip('\n')
                if line.__contains__('Cookie'):
                    cookieKeyAndValues = line.replace('Cookie: ','').replace('Cookie:','').split("; ")
                    for cookieKeyAndValue in cookieKeyAndValues:
                        keyvalues = cookieKeyAndValue.split("=")
                        cookies[keyvalues[0]] = keyvalues[1]
        finally:
            if  not fileObj:
                fileObj.close()

        log.debug(cookies)
        return cookies

    def getHeadersFromFile(file):
        headers = {}
        fileObj = open(file, "r")
        try:
            for line in fileObj.readlines():
                line = line.strip('\n')
                if not line.__contains__('Cookie'):
                    cookieKeyAndValue = line.split(":")
                    headers[cookieKeyAndValue[0].strip()] = cookieKeyAndValue[1].strip()
        finally:
            if not fileObj:
                fileObj.close()
        log.debug(headers)
        return headers