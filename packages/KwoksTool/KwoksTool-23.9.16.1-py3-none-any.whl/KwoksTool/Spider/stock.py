import json
import time
import shutil
from KwoksTool.spider import Browser
from KwoksTool.function import (ProgressBar,ChoiceColumn,GetIpPool)
import pandas as pd
import requests
import numpy as np
from lxml import etree
import os
import re
import random
def GetStocksData(year,array,path,ip=False,type='all'):
    # 函数说明：本函数主要用于采集同花顺行业板块的各类股票数据，可实现一次性采集所有行业；采集单个股票；
    # 参数说明
    # （一）year:采集数据的目标年份的数组，例如：year = [2023, 2022, 2021, 2020, 2019]
    # （二）array:单个采集的代码数组，例如：array = ['1A0001','399001']
    # （三）path:采集完的数据保存的位置，例如：path=r'.\板块数据'
    # （四）ip,是否使用代理Ip，True表示使用
    # （五）type:表示函数功能类型，其中
    # （1）type='all'时：采集所有行业板块的数据
    # （2）type='singel'时：仅仅采集array数组里面的数据
    # （3）type='sum'时：对采集的数据进行合并
    # （六）注意
    # （1）采集过程中ip大概率会被封，无法采集以后退出程序重新运行，如果还是不行就使用代理ip
    # (2)采集，合并，单独采集，需要分开一次一次的运行，采集完以后，最后的合并只需一次
    def spider(num,year,ip=None,type='bk'):
        head={
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
            'Cookie':'log=; Hm_lvt_722143063e4892925903024537075d0d=1687780092,1687863312; Hm_lvt_929f8b362150b1f77b477230541dbbc2=1687780092,1687863312; Hm_lvt_78c58f01938e4d85eaf619eae71b4ed1=1687780092,1687863312; v=AwiFzmPt-LFA3RQ1tmT6rwUk2X0fsW6UThZALcK5V192z6ajasE8S54lEK0R'
        }
        url='http://d.10jqka.com.cn/v4/line/'+str(type)+'_'+str(num)+'/01/'+str(year)+'.js'
        print(url)
        if ip is not None:
            df=requests.get(url,headers=head,proxies=ip)
        else:
            df = requests.get(url, headers=head)
        date=df.text
        date=date.split('{"data":"')[1].split('"})</pre>')[0]
        date=date.split(';')
        result=[]
        for i in range(len(date)):
            son=date[i].split(',')
            result_son=[]
            for son in son:
                result_son.append(son)
            result.append(result_son)
        return result
    def choose():
        # 调用此函数可以获取A股股票的行业分类代码汇总
        # 其中，生成本地文件到资料\板块代码中
        path=r'.\临时资料\板块代码.txt'
        if os.path.exists(path):
            with open(path,encoding='utf-8') as f:
                f=f.read()
                f=f.replace(' ','').replace('\'','"')
                date=json.loads(f)
            return date
        else:
            def plate():
                date = Browser('https://q.10jqka.com.cn/thshy/index/field/199112/order/desc/page/1/ajax/1/',show=True)
                date=date.page_source
                date=etree.HTML(date)
                dates=date.xpath('/html/body/table/tbody/tr')
                record=[]
                for i in range(len(dates)):
                    date_num=(dates[i].xpath('./td[2]/a/@href'))[0]
                    date_num=date_num.split('/')[-2]
                    date_name=dates[i].xpath('./td[2]/a')[0]
                    date_name=date_name.text
                    record.append([str(i+1),date_name,date_num])
                # ======================
                date = Browser('https://q.10jqka.com.cn/thshy/index/field/199112/order/desc/page/2/ajax/1/',show=True)
                date=date.page_source
                date=etree.HTML(date)
                dates=date.xpath('/html/body/table/tbody/tr')
                for ii in range(len(dates)):
                    date_num=(dates[ii].xpath('./td[2]/a/@href'))[0]
                    date_num=date_num.split('/')[-2]
                    date_name=dates[ii].xpath('./td[2]/a')[0]
                    date_name=date_name.text
                    record.append([str(ii+i+1),date_name,date_num])
                # ===================================
                return record
            date=plate()
            with open(path,'w',encoding='utf-8') as f:
                f.write(str(date))
            return date
    def missing(years):
        path=r'.\临时资料\板块\采集'
        names=choose()
        dir=[]
        for name in names:
            for year in years:
                dir.append(name[2]+'-'+str(year)+'.xlsx')
        dirs=(np.sort(os.listdir(path))).tolist()
        need_again=[]
        for i in range(len(dir)):
            if dir[i] not in dirs:
                need_again.append(dir[i])
        return need_again
    def pick(array,year,time_s=1,ip=None,type='bk'):
        if len(array[0])==3:
            def pick_single(year, num):
                for i in year:
                    try:
                        a = spider(num, i,ip=ip,type=type)
                        a = pd.DataFrame(a,columns=['时间','开盘','最高','最低','收盘','总手','金额','','','',''])
                        a.to_excel(r'.\临时资料\板块\采集\\' + str(num) + '-' + str(i) + '.xlsx')
                        time.sleep(time_s)
                    except:
                        # print(i, num)
                        print('\n错误：https://d.10jqka.com.cn/v4/line/bk_' + str(num) + '/01/' + str(i) + '.js')
                        continue
                        time.sleep(time_s)
            for i in range(len(array)):
                array[i]=array[i][2]
                pick_single(year,array[i])
                print(i,len(array)-1,array[i],year[i])
        else:
            def pick_again(num, da):
                (pd.DataFrame(spider(num, da,ip=ip,type=type),columns=['时间','开盘','最高','最低','收盘','总手','金额','','','',''])).to_excel(r'.\临时资料\板块\采集\\' + str(num) + '-' + str(da) + '.xlsx')
                time.sleep(time_s)
            # print('下面为第二次采集的数据')
            for i in range(len(array)):
                print(i,len(array)-1)
                try:
                    pick_again(array[i][0:6],array[i][7:11])
                except:
                    continue
                    time.sleep(time_s)
    def check(year):
        def to_str(year):
            yea=[]
            for son in year:
                yea.append(str(son))
            return yea
        row=[]
        column=year
        date_check=[]
        path=r'.\临时资料\板块\采集'
        files=os.listdir(path)
        names=choose()
        for name in names:
            row.append(name[2])
        for row_son in row:
            date_column_son = []
            for column_son in column:
                if str(row_son)+'-'+str(column_son)+'.xlsx' in files:
                    date_column_son.append(1)
                else:
                    date_column_son.append(0)
            date_check.append(date_column_son)
        (pd.DataFrame(date_check,index=row,columns=to_str(year))).to_excel(r'.\临时资料\板块\采集汇总.xlsx')
        print('采集汇总文件已经保存到\临时资料\板块\采集汇总.xlsx中')
    def sum(path=None,num=None):
        def Merge(num):
            def find_need(date,case):
                result=[]
                for son in date:
                    if case in son:
                        result.append(son)
                return result
            source_path=r'.\临时资料\板块\采集'
            result_path=r'.\临时资料\板块\合并'
            names=find_need(np.sort(os.listdir(source_path)),num)
            file_date=pd.DataFrame()
            for name in names:
                file_path=os.path.join(source_path,name)
                file_date=pd.concat([file_date,ChoiceColumn((pd.read_excel(file_path)),['时间','开盘','最高','最低','收盘','总手','金额'])])
            file_date=file_date.reset_index(drop=True)
            file_name=r'.\\'+num+'.xlsx'
            file_date.to_excel(os.path.join(result_path,file_name))
        if num is None:
            industrys=choose()
            for i in range(len(industrys)):
                Merge(industrys[i][2])
                ProgressBar(i,len(industrys)-1,'正在合并数据'+str(industrys[i][2]))
        else:
            for i in range(len(num)):
                Merge(num[i])
        if path is not None:
            shutil.move(r'.\临时资料\板块\合并',path)
    def DataCollectionPlate(year,ip=False):
        # 输入年份的参数后采集A股板块的所有股票的数据
        # year = [2023, 2022, 2021, 2020, 2019]
        # ip:参数为false时使用代理ip,True时候不使用代理
        # ===================================================
        if len(os.listdir(r'.\临时资料\板块\采集')) == 0:
            print('首次采集，如果首次无法采集任意一个请使用代理Ip')
            array = choose()
            pick(array, year)
            check(year)
        else:
            print('补充采集')
            array = missing(year)
            if ip is not False:
                ip = (GetIpPool())[random.randint(0, 1500)]
                print(ip)
            pick(array, year, ip=ip)
            check(year)
        print('当前完成率为：' + str(
            int((len(os.listdir(r'.\临时资料\板块\采集')) / (len(choose()) * len(year))) * 10000) / 100) + '%')
    def SpecificStocksData(array,year,time_sleep=1):
        # 下载单独的特定代码的股票数据
        # year = [2023, 2022, 2021, 2020, 2019]
        # array=['1A0001','1A0002']
        # ==================================
        for array_son in array:
            for year_son in year:
                print(str(array_son)+'-'+str(year_son))
                date=spider(str(array_son),str(year_son),type='zs')
                (pd.DataFrame(date,columns=['时间','开盘','最高','最低','收盘','总手','金额','','','',''])).to_excel(r'.\临时资料\板块\采集\\' + str(array_son) + '-' + str(year_son) + '.xlsx')
                time.sleep(time_sleep)
        # 合并数据
        def Merge(num):
            def find_need(date,case):
                result=[]
                for son in date:
                    if case in son:
                        result.append(son)
                return result
            source_path=r'.\临时资料\板块\采集'
            result_path=r'.\临时资料\板块\合并'
            names=find_need(np.sort(os.listdir(source_path)),num)
            file_date=pd.DataFrame()
            for name in names:
                file_path=os.path.join(source_path,name)
                file_date=pd.concat([file_date,ChoiceColumn((pd.read_excel(file_path)),[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])])
            file_date=file_date.reset_index(drop=True)
            file_name=r'.\\'+num+'.xlsx'
            file_date.to_excel(os.path.join(result_path,file_name))
        for i in range(len(array)):
            Merge(array[i])
    def main(year,array,type,path,ip=ip):
        print('懒得修复Bug的警告提示：\n当type类型为single时候，如果只是采集这个，会出问题。所以，函数类型的调用必须按照如下顺序：\n\
        all->single->sum\n')
        if type=='all':
            DataCollectionPlate(year, ip=ip)
        elif type=='single':
            SpecificStocksData(array, year)
        elif type=='sum':
            sum()
            sum(path=path,num=array)
            shutil.rmtree(r'.\临时资料')
    def File():
        path1=r'.\临时资料\板块\采集'
        path2 = r'.\临时资料\板块\合并'
        if  not os.path.exists(path1):
            os.makedirs(path1)
        if not os.path.exists(path2):
            os.makedirs(path2)
    File()
    main(year,array,type,path)