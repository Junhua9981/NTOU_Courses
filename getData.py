
#-*- coding: utf-8 -*-
import requests
import json
import os
import csv
from bs4 import BeautifulSoup as bs
from time import sleep
from requests import cookies

from requests.models import Response

ASP_session_ID = '0paqffzn1r15vcpjp43w1ya1'
proxy=[]
GetHeader = {
    'Accept': '*/*',
    #'Cookie': f'GA1.3.462722483.1578900014; ASP.NET_SessionId={ASP_session_ID}',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'User-Agent': r'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

PostHeader = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    #'Cookie': f'GA1.3.462722483.1578900014; ASP.NET_SessionId={ASP_session_ID}',
    'Host': 'ais.ntou.edu.tw',
    'Origin': 'https://ais.ntou.edu.tw',
    'Referer': r'" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
    'sec-ch-ua-mobile': '?0',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': r'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'X-MicrosoftAjax': 'Delta = true',
    'X-Requested-With': 'XMLHttpRequest'
}

mainURL = "https://ais.ntou.edu.tw/Application/TKE/TKE22/TKE2220_01.aspx"
session = None
faculities = {}
ViewState = ''
EventValidation = ''
ViewStateGenerator = ''
CrystalState=''
cookie=None

def saveVSs(soup):
    global ViewState, EventValidation, ViewStateGenerator, CrystalState, cookie
    ViewState = soup.find(id='__VIEWSTATE')['value']
    EventValidation = soup.find(id='__EVENTVALIDATION')['value']
    ViewStateGenerator = soup.find(id='__VIEWSTATEGENERATOR')['value']
    CrystalState=soup.find(id='__CRYSTALSTATECrystalReportViewer')['value']
    cookie=session.cookies


def getSessionID():
    global cookie
    URL = 'http://ais.ntou.edu.tw/outside.aspx?mainPage=LwBBAHAAcABsAGkAYwBhAHQAaQBvAG4ALwBUAEsARQAvAFQASwBFADIAMgAvAFQASwBFADIAMgAyADAAXwAwADEALgBhAHMAcAB4AA=='
    response = session.get(URL, headers=GetHeader, proxies=proxy)
    cookie=session.cookies
    #print(cookie)
    #soup = bs(response.content, 'lxml')
    #saveVSs(soup)


def getFaculityData():
    '''
        找出有哪些faculity
        放到faculities
    '''
    response = session.get(mainURL, headers=GetHeader, proxies=proxy)
    soup = bs(response.content, "lxml")
    saveVSs(soup)
    #cookie=session.cookies
    #print(cookie)
    faculityOPs = soup.find(id='Q_FACULTY_CODE').find_all('option')
    for op in faculityOPs:
        op_text = op.get_text()
        #print(f'ID:{op_text[0:4]} Name:{op_text[5::]}')
        faculities[f'{op_text[0:4]}'] = f'{op_text[5::]}'
    WebPageDownload(response.text, 'aaa')

def getCourseData(faculity, year):
    '''
        獲得科系的所有課程課號 上課時間 教授
        再輸入學期的時候會auto postback
        故須先postback 否則回傳空頁面

    '''
    #if faculity not in faculities:
    #    print('faculity not exisits')
    #    return
    global ViewStateGenerator, ViewState, cookie, CrystalState, EventValidation
    response = session.get(mainURL, headers=PostHeader, proxies=proxy)
    cookie = session.cookies
    soup=bs(response.content, 'lxml')
    saveVSs(soup)
    #print(soup)
    #print(cookie)
    #soup = bs(response.content, 'lxml')

    #ViewState = soup.find(id='__VIEWSTATE')['value']
    #EventValidation = soup.find(id='__EVENTVALIDATION')['value']
    #ViewStateGenerator = soup.find(id='__VIEWSTATEGENERATOR')['value']
    #CrystalState=soup.find(id='__CRYSTALSTATECrystalReportViewer')['value']
    payload = {
        'ScriptManager1': r'AjaxPanel|SetFaculty',
        '__CRYSTALSTATECrystalReportViewer': CrystalState,
        'ActivePageControl': '',
        'ColumnFilter': '',
        'Q_PRESENT_AYEARSMS:': year,
        'Q_FACULTY_CODE': '',
        'Q_GRADE': '',
        'Q_CLASS_ID': '',
        'PC$PageSize': '10',
        'PC$PageNo': '1',
        'PC2$PageSize': '10',
        'PC2$PageNo': '1',
        '__EVENTTARGET': 'SetFaculty',
        '__EVENTARGUMENT': '',
        '__VIEWSTATE': ViewState,
        '__VIEWSTATEGENERATOR': ViewStateGenerator,
        '__VIEWSTATEENCRYPTED': '',        
        '__EVENTVALIDATION': EventValidation,
        '__ASYNCPOST': 'true'
    }
    print(payload)
    #print(cookie)
    response = session.post(mainURL, data=payload, headers=PostHeader, proxies=proxy, cookies=cookie)
    print(response)
    soup=bs(response.content, 'lxml')
    print('===========================================')
    print('||                                        ||')
    print('||            FIRST   POST                ||')
    print('||                                        ||')
    print('===========================================')
    #print(soup)

    response = session.get(mainURL, headers=PostHeader, proxies=proxy, cookies=cookie)
    #print(response)
    ViewState = response.text[((response.text.find(r'|__VIEWSTATE|')+13)):( (response.text.find('|', (response.text.find(r'|__VIEWSTATE|')) )+19) ) ]
    print('type:', end='')
    print(type(response.text))
    print('Viewstate:'+ViewState)
    EventValidation = response.text[ (response.text.find(
        r'|__EVENTVALIDATION|')+19) : (response.text.find( r'|', response.text.find(
            '|__EVENTVALIDATION|')+25) ) ]
    print('EventVali:'+EventValidation)
    soup = bs(response.content, 'lxml')
    #saveVSs(soup)
    payload = {
        'ScriptManager1': 'AjaxPanel|QUERY_BTN1',
        '__CRYSTALSTATECrystalReportViewer': CrystalState,
        'ActivePageControl': '',
        'ColumnFilter': '',
        'Q_PRESENT_AYEARSMS:': year,
        'Q_FACULTY_CODE': faculity,
        'Q_GRADE': '',
        'Q_CLASS_ID': '',
        'PC$PageSize': '150',
        'PC$PageNo': '1',
        'PC2$PageSize': '150',
        'PC2$PageNo': '1',
        '__EVENTTARGET':'',
        '__EVENTARGUMENT':'',
        '__VIEWSTATE': ViewState,
        '__VIEWSTATEGENERATOR': ViewStateGenerator,
        '__EVENTVALIDATION': EventValidation,
        '__VIEWSTATEENCRYPTED': '',
        '__ASYNCPOST': 'true',
        'QUERY_BTN1': '查詢'
    }
    response = session.post(mainURL, data=payload, headers=PostHeader, proxies=proxy, cookies=cookie)
    print(response)
    soup = bs(response.content, 'lxml')
    print('===========================================')
    print('||                                        ||')
    print('||            SECOND   POST               ||')
    print('||                                        ||')
    print('===========================================')
    #print(soup)
    #saveVSs(soup)

    WebPageDownload(response.text, 'testttt')
    #print("Download success")


    clazzNames = soup.find(id="grid-scroll").find('div').find('table').find_all('tr')
    clazzNames = clazzNames[1:] #裁切掉頭
    nowClazz = ''
    for clazz in clazzNames:
        expidx = 0
        td = clazz.find_all('td')
        if td[0].has_attr('rowspan'):   #如果是最前面那個 有科系年級
            nowClazz = td[0].string
            expidx = 1
        print(
            f"{nowClazz} | {td[0+expidx].string} |{td[1+expidx].string:　^12}| {td[2+expidx].string} | {td[8+expidx].string} | {td[9+expidx].string} ")


def WebPageDownload(text, name):
    '''
    下載到{name}.html裡面
    '''
    ff = open(f"{name}.html", 'w', encoding='utf-8')
    ff.writelines(text)
    ff.close()
    print(f'download {name}.html success')


if __name__ == "__main__":
    session = requests.session()
    Ip = input('Proxy IP(Socks4):')
    Port=input('Port:')
    proxy = {'http': f"socks4://{Ip}:{Port}",
             'https': f"socks4://{Ip}:{Port}"}
    getSessionID()
    #ASP_session_ID=input("ASP_session_ID:")

    #getFaculityData()
    #print(faculities)
    faculity=input('faculity')
    year=input('year:')
    getCourseData(faculity=faculity, year=year)
    print('===========================================')
    print('||                                        ||')
    print('||            END                         ||')
    print('||                                        ||')
    print('===========================================')
    '''
    獲得所有科系的課程資料 但是沒有上課時間
    for fac in faculities:
        #print(type(fac))
        print(fac)
        getCourseData(session, degree='0', faculity=fac)
        sleep(10)
    '''
    #getCourseDetail('0', '0700', 1)
