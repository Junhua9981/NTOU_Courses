#-*- coding: utf-8 -*-
import requests
import json
import os
import csv
from bs4 import BeautifulSoup as bs
from time import sleep


def strB2Q(ustring):
    """把字串全形轉半形"""
    ss = []
    for s in ustring:
        rstring = ""
        for uchar in s:
            inside_code = ord(uchar)
            if inside_code == 32:  # 全形空格直接轉換
                inside_code = 12288
            elif (inside_code >= 33 and inside_code <= 126):  # 全形字元（除空格）根據關係轉化
                inside_code += 65248
            rstring += chr(inside_code)
        ss.append(rstring)
    return ''.join(ss)



#with open(r'D:\Download\NCNU_Course-master\NCNU_Course-master\授課時間表查詢列印.html',encoding="utf-8") as fp:
#    soup = bs(fp, 'lxml')
#
#clazzNames = soup.find(id="grid-scroll").find('div').find('table').find_all('tr')
#clazzNames=clazzNames[1:]
##print(f'{clazzNames}')
#nowClazz = ''
#for clazz in clazzNames:
#    expidx = 0
#    td = clazz.find_all('td')    
#    if td[0].has_attr('rowspan'):
#        nowClazz = td[0].string
#        expidx = 1
#    print(f"{nowClazz} | {td[0+expidx].string} |{strB2Q(td[1+expidx].string):　^16}| {td[2+expidx].string} | {td[8+expidx].string:^15} | {td[9+expidx].string} ")
with open(r'D:\Download\NCNU_Course-master\NTOU\rewrite\test.txt', encoding="utf-8") as fp:
    s=fp.read()
ViewState = s[(s.find('|__VIEWSTATE|')+13):(s.find('|',s.find('|__VIEWSTATE|')+15))]
print('Viewstate:'+ViewState)
