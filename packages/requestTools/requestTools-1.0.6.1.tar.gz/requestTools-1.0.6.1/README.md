## 使用概述

对于常见的http request请求进行了封装，通过实现NormalHttpRequestProcessor、PageDataHttpRequestProcessor，即可轻松完成http请求，并且能获取到http请求后的页面结果数据，目前只支持json的返回结果数据解析。

## 创建cookiefile文件夹
在工程代码的工程目录下，创建cookiefile文件夹，建立独立的cookie文件，例如baidu.txt，在baidu.txt中，将浏览器cookie和header信息拷贝到文件夹中，chrome浏览器中F12后，在NetWork中拷贝Request Headers中内容即可，例如：
```
Accept: */*
Accept-Encoding: gzip, deflate, br
Accept-Language: zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7
Connection: keep-alive
Cookie: BIDUPSID=EAFB8E1DB0216DE6FCD0FEF72E8320D0; PSTM=1662445619; BAIDUID=EAFB8E1DB0216DE68D0719E5A758651F:FG=1; BD_UPN=123253; BDSFRCVID=ZNKOJeC62ZTrCobj_pMOUi4cxm5rbsOTH6aomrJTuV5jDUsCKBVlEG0P3f8g0KuMzkoeogKKKgOTHICF_2uxOjjg8UtVJeC6EG0Ptf8g0f5; H_BDCLCKID_SF=JJkO_D_atKvDqTrP-trf5DCShUFsWf5JB2Q-XPoO3KJnHtIRMRrHM-Pf34bT5j5r0CrmQfbgylRp8P3y0bb2DUA1y4vp5MnqQeTxoUJ25JbhVlboqj5Ah--ebPRiB-b9QgbA5hQ7tt5W8ncFbT7l5hKpbt-q0x-jLTnhVn0MBCK0MC09j6KhDTPVKgTa54cbb4o2WbCQMPoz8pcN2b5oQT81-queaJcKtHOW-qOxKDQdEJoJKlOUWfAkXpJvQnJjt2JxaqRCKhv-Sl5jDh3Mb40004Oie6jzaIvy0hvcWb3cShnVLUjrDRLbXU6BK5vPbNcZ0l8K3l02V-bIe-t2XjQhjGtOtjDttb3aQ5rtKRTffjrnhPF3X-PdXP6-hnjy3bRx34Ib2tTHhR6c3xbm-6KTLf5mbq3RymJ42-39LPO2hpRjyxv4-UPB34oxJpOJ5DntbqbcHCoADb3vbURvyP-g3-7A3M5dtjTO2bc_5KnlfMQ_bf--QfbQ0hOhqP-jBRIE_D0yJD_hhIvPKITD-tFO5eT22-us3ecR2hcHMPoosIJj-Ju5MRF_-JJWLfJTKJcr5Ron-fbUoqRHXnJi0btQDPvxBf7pK23q-q5TtUJMeRbG0xOvqjDlhMJyKMniWKv9-pnY0hQrh459XP68bTkA5bjZKxtq3mkjbPbDfn028DKuj5KaDjcWeaus2-5h2C7-stnaKRrOK4bvK5RAXxPgyxomtjjzQTrmWbo_X-JY8U5Yj-bWhjLX-lb9LUkqKCOLQqcmbxLhjlbaKUbvLlKjQttjQTJhfIkja-5zMJvoeJ7TyURvbU47y-rm0q4Hb6b9BJcjfU5MSlcNLTjpQT8r5MDOK5OhJRQ2QJ8BtC8MMCoP; BDORZ=B490B5EBF6F3CD402E515D22BCDA1598; delPer=0; BD_CK_SAM=1; PSINO=5; BA_HECTOR=8l0k81000h2ha50lah8k9bug1hlc0rc1a; ZFY=o:B8Dk:AKnWhzUFtPdX4dS4jc2yZ0S3QwYrpvDkO:Ai5aA:C; BAIDUID_BFESS=EAFB8E1DB0216DE68D0719E5A758651F:FG=1; BDSFRCVID_BFESS=ZNKOJeC62ZTrCobj_pMOUi4cxm5rbsOTH6aomrJTuV5jDUsCKBVlEG0P3f8g0KuMzkoeogKKKgOTHICF_2uxOjjg8UtVJeC6EG0Ptf8g0f5; H_BDCLCKID_SF_BFESS=JJkO_D_atKvDqTrP-trf5DCShUFsWf5JB2Q-XPoO3KJnHtIRMRrHM-Pf34bT5j5r0CrmQfbgylRp8P3y0bb2DUA1y4vp5MnqQeTxoUJ25JbhVlboqj5Ah--ebPRiB-b9QgbA5hQ7tt5W8ncFbT7l5hKpbt-q0x-jLTnhVn0MBCK0MC09j6KhDTPVKgTa54cbb4o2WbCQMPoz8pcN2b5oQT81-queaJcKtHOW-qOxKDQdEJoJKlOUWfAkXpJvQnJjt2JxaqRCKhv-Sl5jDh3Mb40004Oie6jzaIvy0hvcWb3cShnVLUjrDRLbXU6BK5vPbNcZ0l8K3l02V-bIe-t2XjQhjGtOtjDttb3aQ5rtKRTffjrnhPF3X-PdXP6-hnjy3bRx34Ib2tTHhR6c3xbm-6KTLf5mbq3RymJ42-39LPO2hpRjyxv4-UPB34oxJpOJ5DntbqbcHCoADb3vbURvyP-g3-7A3M5dtjTO2bc_5KnlfMQ_bf--QfbQ0hOhqP-jBRIE_D0yJD_hhIvPKITD-tFO5eT22-us3ecR2hcHMPoosIJj-Ju5MRF_-JJWLfJTKJcr5Ron-fbUoqRHXnJi0btQDPvxBf7pK23q-q5TtUJMeRbG0xOvqjDlhMJyKMniWKv9-pnY0hQrh459XP68bTkA5bjZKxtq3mkjbPbDfn028DKuj5KaDjcWeaus2-5h2C7-stnaKRrOK4bvK5RAXxPgyxomtjjzQTrmWbo_X-JY8U5Yj-bWhjLX-lb9LUkqKCOLQqcmbxLhjlbaKUbvLlKjQttjQTJhfIkja-5zMJvoeJ7TyURvbU47y-rm0q4Hb6b9BJcjfU5MSlcNLTjpQT8r5MDOK5OhJRQ2QJ8BtC8MMCoP; H_PS_PSSID=37545_36555_37584_36885_37623_36807_36786_37540_37500_37581_26350_37479_37460; BD_HOME=1; COOKIE_SESSION=3_1_9_9_4_9_1_0_9_9_0_1_181685_0_0_0_1666415270_1666415261_1666598270%7C9%230_1_1666415257%7C1; RT="z=1&dm=baidu.com&si=y49dwif0dul&ss=l9miq93l&sl=4&tt=2sg&bcn=https%3A%2F%2Ffclog.baidu.com%2Flog%2Fweirwood%3Ftype%3Dperf&ld=fyj&ul=hrzh&hd=hs15"; ab_sr=1.0.1_NjE3ZjJjOTNiYmNmZTg2ZDE3NzA3NzA0NjBiZDczNTFlYmZmNTEwYzAxYjFmNjM0YWRiMTk0M2FiNGJlNzAzNDFkYWNiZDM3MjNkMGE3ZDgwNTkzZDlkN2FhYWYwMDllMWU3YmEwMDBmM2I1MWZmOTZjMTk5Yjc3MDlmODViNTNlMGJmYzI5MjBjMTAxOWMwZDNjYWQxZmRhYmJiMTZiZA==; H_PS_645EC=0b50uo%2BuDFbacXzWa6iug1SXj6laCPoD2wbL8zjlrPkpkgwfjQbCuw6ERYs; BDSVRTM=168; channel=baidusearch; baikeVisitId=33e07bf7-61ff-4ec1-9fd1-15d5ad5badf7; WWW_ST=1666612064540
Host: www.baidu.com
is_pbs: x%20x%20x
is_referer: https://www.baidu.com/s?ie=utf-8&f=8&rsv_bp=1&rsv_idx=1&tn=baidu&wd=x%20x%20x&fenlei=256&rsv_pq=0x9048019600029174&rsv_t=5775V%2BOBPsgxMEW9xagSvt08ycYJf%2FPda7A3O037Nj37yAohPBtn3gSow7Pn&rqlang=en&rsv_enter=0&rsv_dl=tb&rsv_sug3=4&rsv_sug1=3&rsv_sug7=101&rsv_btype=i&inputT=5685&rsv_sug4=5749
is_xhr: 1
Ps-Dataurlconfigqid: 0x9048019600029174
Referer: https://www.baidu.com/s?ie=utf-8&f=8&rsv_bp=1&rsv_idx=1&tn=baidu&wd=x%20x%20x&fenlei=256&oq=x%2520x%2520x&rsv_pq=e6bcf3a300147260&rsv_t=0b50uo%2BuDFbacXzWa6iug1SXj6laCPoD2wbL8zjlrPkpkgwfjQbCuw6ERYs&rqlang=cn&rsv_enter=0&rsv_dl=tb&rsv_btype=t
sec-ch-ua: "Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"
sec-ch-ua-mobile: ?0
sec-ch-ua-platform: "macOS"
Sec-Fetch-Dest: empty
Sec-Fetch-Mode: cors
Sec-Fetch-Site: same-origin
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36
X-Requested-With: XMLHttpRequest
```

## 实现NormalHttpRequestProcessor子类
```
from com.http.HttpRequestProcessor import NormalHttpRequestProcessor
from com.http.HttpRequestUtils import MethodEnum


class XXXNormalHttpRequestProcessor(NormalHttpRequestProcessor):
    """一个基本的http请求处理实现类
    该类重新实现了setCookieFileName,setUrl,setMethod,setFormValues5个抽象方法
    """
    # 设置cookie文件名称
    def setCookieFileName(self):
        return "xx.txt"

    # 设置Url
    def setUrl(self, dynamicParams=None):
        return "xxx"

    # 设置方法
    def setMethod(self):
        return MethodEnum.XXXX

    # 设置表单信息
    def setStaticFormValues(self):
        # 固定不变的请求参数
        formValues = {
            'key1':'value1',
            'key2':'value2',
            'key3':'value3'          
        }
        return formValues


if __name__ == '__main__':
    xxxNormalHttpRequestProcessor = XXXNormalHttpRequestProcessor()
    xxxNormalHttpRequestProcessor.getResponse()


```

## 实现PageDataHttpRequestProcessor子类
```
from com.http.HttpRequestProcessor import PageDataHttpRequestProcessor
from com.http.HttpRequestUtils import MethodEnum



class XXXPageDataHttpRequestProcessor(PageDataHttpRequestProcessor):
    """一个基本的分页爬取所有页面数据的HTTP请求处理实现类
       该类重新实现了setCookieFileName,setUrl,setMethod,setFormValues,setCurrentPageNumberKey,getTotal,getCurrentPageDatas,parseRowValues 9个抽象方法
    """

    # 设置cookie文件名称
    def setCookieFileName(self):
        return "xxxxx.txt"

    # 设置Url
    def setUrl(self, dynamicParams=None):
        return "xxxxx"

    # 设置执行方法
    def setMethod(self):
        return MethodEnum.XXX
    
    # 设置表单信息
    def setStaticFormValues(self):
        # 固定不变的请求参数
        formValues = {
            "key1":"value1",
            "key2":"value2",
            "key3":"value3"          
        }
        return formValues

    # 设置当前页码属性名称
    def setCurrentPageNumberKey(self):
       # 根据实际情况调整
       return "currentPage"

    # 获取总条数
    def getTotal(self, pageJsonObj):
        # 根据实际情况调整
        return int(pageJsonObj['data']['paging']['totalCount'])

    # 获取一页所有的行
    def getCurrentPageDatas(self, pageJsonObj):
        # 根据实际情况调整
        return pageJsonObj['data']['tableData']

    #  获取每行各字段的数据
    def parseRowValues(self, rowJsonObj):
        # 根据实际情况调整
        return rowJsonObj


if __name__ == '__main__':
    xxxPageDataHttpRequestProcessor = XXXPageDataHttpRequestProcessor()
    allDatas = xxxPageDataHttpRequestProcessor.getResponse()
```