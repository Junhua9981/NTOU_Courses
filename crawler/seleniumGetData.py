from urllib.parse import uses_fragment
from bs4 import element
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup as bs
from time import sleep
import json

faculities = {}
courses=[]

def setupBrowser(useProxy):
    opts = Options()

    opts.add_argument("--incognito")  # 無痕模式

    user_agent = 'Mozilla/5.0 (X11; CrOS i686 4319.74.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.57 Safari/537.36'
    opts.add_argument(f"user-agent={user_agent}")

    useProxy=useProxy.lower()
    if useProxy=='socks4' or 'http':
        proxyIP = input('proxy IP:')           # set up proxy
        proxyPort = input('proxy Port:')
        opts.add_argument(f'--proxy-server={useProxy}://'+proxyIP+':'+proxyPort)

    browser = webdriver.Chrome(
        r'crawler\chromedriver.exe', chrome_options=opts)
    return browser


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


def getFaculty(soup):
    """get faculties in 開課系所 OPINIONS

    Args:
        soup (bs4 souped): mainURL's page soup
    """
    global faculities
    faculityOPs = soup.find(id='Q_FACULTY_CODE').find_all('option')
    del faculityOPs[0]
    for op in faculityOPs:
        op_text = op.get_text()
        #print(f'ID:{op_text[0:4]} Name:{op_text[5::]}')
        faculities[f'{op_text[0:4]}'] = f'{op_text[5::]}'


def setYear(browser):
    """set year in 查詢學期

    Args:
        browser (browser obj): selenium browser object
    """
    year = browser.find_element_by_xpath(r'//*[@id="Q_PRESENT_AYEARSMS"]')
    year.send_keys('1101')
    # year.send_keys(Keys.ENTER)


def selectFaculity(browser, faculty):
    """select Faculity in 開課系所

    Args:
        browser (browser obj): selenium browser object
        faculty (4letters string): select faculity value
    """
    facultySelect = Select(browser.find_element_by_xpath(
        r'//*[@id="Q_FACULTY_CODE"]'))
    # faculty=input('faculty:')

    #faculty = str(input('Fac:'))
    facultySelect.select_by_value(faculty)


def clickSearch(browser):
    """click 查詢 button

    Args:
        browser (browser obj): selenium browser object
    """
    search = browser.find_element_by_xpath(r'//*[@id="QUERY_BTN1"]')
    search.click()


def setRows(browser):
    """set 筆數

    Args:
        browser (browser obj): selenium browser object
    """
    inRows = browser.find_element_by_xpath('//*[@id="PC_PageSize"]')
    inRows.send_keys(Keys.CONTROL + "a")  # 只要數值為空網頁就會一直alert卡死== 只好這樣寫
    inRows.send_keys('2350')          #全部2341
    inRows.send_keys(Keys.ENTER)


def getCourseData(soup):
    """get course data
        include faculity courceNum teacher time ... 

    Args:
        soup (bs4ed soup): mainURL's page source
    """

    global courses
    clazzNames = soup.find(
        id="grid-scroll").find('div').find('table').find_all('tr')
    clazzNames = clazzNames[1:]
    # print(f'{clazzNames}')
    nowClazz = ''
    rows = 0

    for clazz in clazzNames:
        expidx = 0
        td = clazz.find_all('td')

        if td[0].has_attr('rowspan'):
            nowClazz = td[0].string
            expidx = 1
            rows = int(td[0].get('rowspan'))
            # print(f'rows:{rows}')
        elif rows < 1:
            nowClazz = td[0].string
            expidx = 1
        else:
            expidx = 0

        courseObj={}
        courseObj['number'] = td[0+expidx].string                       # 課號
        courseObj['name'] = td[1+expidx].string                         # 課名
        courseObj['department'] = nowClazz[: nowClazz.find(u'年')-2]    # 系所
        courseObj['grade'] =  nowClazz[nowClazz.find(u'年')-1]          # 年級
        courseObj['class'] = nowClazz[nowClazz.find(u'班')-1]           # 班別
        courseObj['professor'] = td[9+expidx].string                    # 教授
        courseObj['place'] = td[7+expidx].string                        # 上課位置
        courseObj['time'] = td[8+expidx].string                         # 上課時間
        if td[2+expidx].string == '通':
            courseObj['sorting'] = f'{td[2+expidx].string}[{td[1+expidx].string[-3:-1]}]' #選修必修
        else:
            courseObj['sorting'] = td[2+expidx].string

        print(
            f"{courseObj['number']} | {courseObj['name']} | {courseObj['department']} | {courseObj['grade']} | {courseObj['class']} | {courseObj['professor']} | {courseObj['place']} | {courseObj['time']} | {courseObj['sorting']}")

    #    if td[2+expidx].string == '通':
    #        print(
    #            f"{nowClazz[: nowClazz.find(u'年')-2]}| {nowClazz[nowClazz.find(u'年')-1]} | {nowClazz[nowClazz.find(u'班')-1]} | {td[0+expidx].string} |{strB2Q(td[1+expidx].string):　^20}| {td[2+expidx].string}[{td[1+expidx].string[-3:-1]}] | {td[8+expidx].string:^15} | {td[9+expidx].string}")
    #        #           系所                                       年                                    班                             課號                   課名                                選別                                                    上課時間                教授名稱
    #    else:
    #        print(
    #            f"{nowClazz[: nowClazz.find(u'年')-2]}| {nowClazz[nowClazz.find(u'年')-1]} | {nowClazz[nowClazz.find(u'班')-1]} | {td[0+expidx].string} |{strB2Q(td[1+expidx].string):　^20}| {td[2+expidx].string: ^5} | {td[8+expidx].string:^15} | {td[9+expidx].string}")
        #           系所                                           年                                    班                             課號                   課名                                選別                        上課時間                教授名稱
        
        courses.append(courseObj)
        
        rows -= 1
    

def printFaculity(dct):
    print('科系:')
    for num, name in sorted(dct.items()):
        print(f'{num} : {name}')

if __name__ == "__main__":
    #input("press any key to start...")
    #geckoDriver = r'D:\Download\NCNU_Course-master\NTOU\geckodriver.exe'
    # browser=webdriver.Firefox(geckoDriver)

    useProxy=str(input('Wut type Proxy:'))
    browser = setupBrowser(useProxy=useProxy)

    #get SessionID cookies
    browser.get(r'https://ais.ntou.edu.tw/outside.aspx?mainPage=LwBBAHAAcABsAGkAYwBhAHQAaQBvAG4ALwBUAEsARQAvAFQASwBFADIAMgAvAFQASwBFADIAMgAyADAAXwAwADEALgBhAHMAcAB4AA==')
    
    mainURL = r"https://ais.ntou.edu.tw/Application/TKE/TKE22/TKE2220_01.aspx"
    browser.get(mainURL)



    setYear(browser=browser)
    sleep(1)
    setRows(browser=browser)
    sleep(1)

    #soup = bs(browser.page_source)
    getFaculty(soup=bs(browser.page_source,'lxml'))
    printFaculity(faculities)

    try:
        element = WebDriverWait(browser, 60).until(
            EC.presence_of_element_located(
                (By.XPATH, r'//*[@id="DataGrid"]/tbody/tr[1]'))
        )
    finally:
        print("Render Page Success")
    #soup = bs(browser.page_source, 'lxml')
    getCourseData(soup=bs(browser.page_source, 'lxml'))
    sleep(2)

    #faculity = str(input('Faculity:'))


#    for faculity, facName in sorted(faculities.items()): 
#        print('faculity'+ faculity + ' '+ facName)
#        selectFaculity(browser=browser, faculty=faculity)
#        sleep(2)
#
#        # browser.implicitly_wait(10)
#        # sleep(2)
#        setRows(browser=browser)
#        sleep(1)
#
#        try:
#            element = WebDriverWait(browser, 15).until(
#                EC.presence_of_element_located(
#                    (By.XPATH, r'//*[@id="DataGrid"]/tbody/tr[1]'))
#            )
#        finally:
#            print("Render Page Success")
#
#
#
#        #soup = bs(browser.page_source, 'lxml')
#        getCourseData(soup=bs(browser.page_source, 'lxml'))
#        sleep(2)
    # print(soup)



    with open('output.json', 'w', encoding='utf8') as fp:
        json.dump(courses, fp, ensure_ascii=False)

    print(len(courses))
