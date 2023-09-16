import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from datetime import datetime
import tushare as ts
import re
from KwoksTool.function import (ProgressBar,ChoiceColumn)
def Browser(url, show=False):
    options = webdriver.ChromeOptions()
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    if show is False:
        options.add_argument('--headless')
    driver = webdriver.Chrome(options=options, service=Service("chromedriver.exe"))
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
      Object.defineProperty(navigator, 'webdriver', {
        get: () => undefined
      })
    """
    })
    # driver.maximize_window()
    driver.minimize_window()
    driver.get(url)
    return driver
def PlateComponentStocks(PlateInfoName, url,code):
    # code:tushure的秘钥
    # url:文件保存的路径
    # plateinfoname:股票的板块代码
    def GetPlateSon(stock_num):
        def get_stock_name(date, num):
            def get_re_name(date):
                date = '<td><a href="http://stockpage.10jqka.com.cn/' + date + '" target="_blank">\D*</a'
                return date

            a = (re.findall(re.compile(str(get_re_name(str(num)))), date))
            '''<td><a href="http://stockpage.10jqka.com.cn/000001" target="_blank">平安银行</a>'''
            a = re.findall(r'>\D*</a', a[0])[0]
            a = a.replace('>', '').replace('</a', '')
            return a

        date = (Browser('http://q.10jqka.com.cn/thshy/detail/field/199112/order/desc/page/1/ajax/1/code/' + stock_num,
                        show=True)).page_source
        date_arr = re.findall(r'\d{6}<', date)
        web_pages = date
        date_name = []
        if len((re.findall(r'>\d*/\d*<', date))) == 0:
            for i in range(len(date_arr)):
                date_arr[i] = date_arr[i].replace('<', '')
                date_name.append(get_stock_name(date, date_arr[i]))
            return date_arr
        else:
            page = (re.findall(r'>\d*/\d*<', date))[0].split('/')[1].replace('<', '')
            for i in range(2, int(page) + 1):
                web_page = (Browser(
                    'http://q.10jqka.com.cn/thshy/detail/field/199112/order/desc/page/' + str(i) + '/ajax/' + str(
                        i) + '/code/' + stock_num, show=True)).page_source
                web_pages = web_pages + web_page
                date_arr = date_arr + re.findall(r'\d{6}<', web_page)
            for i in range(len(date_arr)):
                date_arr[i] = date_arr[i].replace('<', '')
                date_name.append(get_stock_name(web_pages, date_arr[i]))
            result = {'代码': date_arr, '名称': date_name}
            return result
    def FindCode(codes):
        result = []
        pro = ts.pro_api(ApiCode)
        data = pro.daily(ts_code='')
        data = data.sort_values(by='ts_code')
        data = data['ts_code'].T.values.tolist()
        for i in range(0, len(data)):
            if data[i][:6] == codes:
                result.append(data[i])
        return result
    a =GetPlateSon(PlateInfoName)
    ApiCode=code
    pro = ts.pro_api(ApiCode)
    print('正在下载' + str(PlateInfoName) + '板块的股票信息')
    for i in range(0, len(a['代码'])):
        try:
            code = FindCode(a['代码'][i])
            for son in code:
                data = pro.daily(ts_code=son)
                data = data.rename(
                    columns={'open': '开盘', 'close': '收盘', 'high': '最高', 'low': '最低', 'amount': '总手',
                             'vol': '金额', 'trade_date': '时间'})
                data = ChoiceColumn(data, ['开盘', '最高', '最低', '收盘', '总手', '金额', '时间'])
                data = data.sort_values(by='时间')
                data = pd.DataFrame(data, columns=['开盘', '最高', '最低', '收盘', '总手', '金额', '时间'])
                data = data.reset_index(drop=True)
                # ==========================================
                data.to_excel(r'{}\{}.xlsx'.format(url, a['代码'][i]))
                ProgressBar(i, len(a['代码']), a['名称'][i])
        except:
            print(i,'错误')
            continue