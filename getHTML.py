# -*- encoding: utf-8 -*-
'''
@File    :   getHTML.py
@Time    :   2021/01/28 03:28:28
@Author  :   Geralt 
@Version :   1.0
@Contact :   superj0529@gmail.com
'''

# here put the import lib
import re
import urllib
from http import cookiejar


def getLt(response): 
    #获取流水号
    pattern = re.compile(r"LT-[0-9]*-[0-9a-zA-Z]*-tpass")
    lt = pattern.findall(response)[0]
    return lt

def getHTML(mid,ps):
    cookie = cookiejar.CookieJar()
    handler = urllib.request.HTTPCookieProcessor(cookie)
    opener = urllib.request.build_opener(handler)
    loginurl = "https://ehall.neu.edu.cn/infoplus/login?retUrl=http://219.216.96.4/eams/courseTableForStd.action"
    response1 = opener.open(loginurl)
    decode_txt1=response1.read().decode()
    lt = getLt(decode_txt1)
    id = mid
    password = ps
    values1 = {
        "_eventId":"submit",
        "execution":"e1s1",
        "lt":lt,
        "pl":str(len(password)),
        "rsa":id+password+lt,
        "ul":str(len(id))
    }
    postdata1 = urllib.parse.urlencode(values1).encode("utf-8")
    opener.addheaders = [("User-Agent",'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36')]
    response2 = opener.open(response1.geturl(), postdata1)
    decode_txt2 = response2.read().decode()
    ids_p = re.compile(r"bg\.form\.addInput\(form,\"ids\",\"(\w.*?)\"")
    ids = ids_p.findall(decode_txt2)[0]
    print("login successfully!")
    formdata={
    'ids':ids,
    'ignoreHead':'1',
    'semester.id':'56',
    'setting.kind':'std',
    'showPrintAndExport':'1',
    'startWeek':''
    }
    postdata2 = urllib.parse.urlencode(formdata).encode("utf-8")
    print("receiving courseTable page...")
    response3 = opener.open('http://219.216.96.4/eams/courseTableForStd!courseTable.action', postdata2)
    print(response3.status)
    return response3.read().decode()


if __name__ == "__main__":
    with open(file='table.html',mode='a',encoding='utf-8') as f:
        f.writelines(getHTML('',''))