import pandas as pd
import requests
import random
from KwoksTool.source.IpPool import GetIpPool
import email
import imaplib
import re
from email.header import decode_header
import execjs
import json
import mimetypes
import smtplib   # 发送邮件模块
from email import encoders
from email.mime.multipart import MIMEMultipart    # 使用MIMEMultipart来标示这个邮件是多个部分组成的
from email.mime.base import MIMEBase
from email.mime.text import MIMEText   # 定义邮件内容
import  datetime
from email.utils import formataddr
import os.path
import sys
from zipfile import ZipFile
import zipfile
import os
def GetCityNumFromLiepin(place):
    # place:城市名称，例如GetCityNumFromLiepin('温州')
    # 返回值:城市代码的数组，例如['300060010', '300060090']
    ip = GetIpPool()
    ip = ip[random.randint(0, len(ip))]
    print('猎聘网正在查询城市编码')
    case=1
    OutNum=1
    while case==1:
        try:
            sheng = place[:place.find('省')]
            shi = place[place.find('省') + 1:place.find('市')]
            url = "https://apidok.liepin.com/api/com.liepin.bd.p.v3.get-all-dq"
            data = "sceneCode=6&from=component"
            header = {
                "Accept": "application/json, text/plain, */*",
                "Content-Type": "application/x-www-form-urlencoded",
                "X-Client-Type": "web",
                "X-Fscp-Fe-Version": "",
                "X-Fscp-Version": "1.1",
                "X-Fscp-Std-Info": "{\"client_id\": \"40108\"}",
                "X-Requested-With": "XMLHttpRequest",
                "X-Fscp-Trace-Id": "8136730b-00b0-4daa-b975-59728e3c2a5a",
                "X-XSRF-TOKEN": "1vL6nJjVRCu01PAwwQmdEg"
            }
            data = requests.post(url, data=data, headers=header).json()
            name = data['data']['data']['city']['list']
            num = data['data']['data']['city']['relations']
            name = str(name)
            citysNum = num[str(((name.split(sheng)[0]).split('\'code\': \'')[-1])[:3])]
            for son in citysNum:
                qu = ((name.split(str(shi))[0]).split('\'code\': \'')[-1])[:6]
                cityName = \
                (((name.split('\'' + str(qu) + '\', \'seoUri\': \'')[1]).split('\', \'category\'')[0])).split('\'')[-1]
                if son == qu:
                    result = num[qu]
                    print('已经为你找到' + sheng + '省' + cityName + '市的所有区县，即将为你查询')
                    break
                else:
                    result = []
            return result
            case=2
        except:
            OutNum=OutNum+1
            if OutNum==10:
                print('抱歉，城市编码查询失败')
                case=2
            else:
                continue
def GetCityNumFromBossZhiPing(city,proxies=False):
    # city:输入省市县的城市名称，例如：'浙江省宁波市'
    # proxies:是否使用Ip代理
    # 返回值：城市代码的数组，例如：['101210400']
    ip = GetIpPool()
    ip = ip[random.randint(0, len(ip))]
    city=(city.split('省')[1]).split('市')[0]
    print('boss直聘查询说明\n本功能只能通过城市名字查询一个，关键词例如(宁波)，返回结果不是区的字典，只是当前城市代码。\n正在查询Boss的城市代码')
    if proxies is True:
        res = requests.get('https://www.zhipin.com/wapi/zpCommon/data/cityGroup.json',proxies=ip).json()
    else:
        res = requests.get('https://www.zhipin.com/wapi/zpCommon/data/cityGroup.json').json()
    res = str(res['zpData']['cityGroup'])
    res = (res.split(str(city))[0]).split('code\': ')[-1].replace(', \'name\': \'', '')
    res=[str(res)]
    return res
def GetCityNameFromLiepin(num,proxies=False):
    # num:城市代码，例如：GetCityNameFromLiepin('300060010',proxies=False)
    # proxies:是否使用代理ip,防止Ip被封禁
    # 返回值：城市名称，例如：阿克苏市
    ip = GetIpPool()
    ip = ip[random.randint(0, len(ip))]
    case = 1
    while case == 1:
        try:
            sheng = num[:num.find('省')]
            shi = num[num.find('省') + 1:num.find('市')]
            url = "https://apidok.liepin.com/api/com.liepin.bd.p.v3.get-all-dq"
            data = "sceneCode=6&from=component"
            header = {
                "Accept": "application/json, text/plain, */*",
                "Content-Type": "application/x-www-form-urlencoded",
                "X-Client-Type": "web",
                "X-Fscp-Fe-Version": "",
                "X-Fscp-Version": "1.1",
                "X-Fscp-Std-Info": "{\"client_id\": \"40108\"}",
                "X-Requested-With": "XMLHttpRequest",
                "X-Fscp-Trace-Id": "8136730b-00b0-4daa-b975-59728e3c2a5a",
                "X-XSRF-TOKEN": "1vL6nJjVRCu01PAwwQmdEg"
            }
            if proxies is True:
                data = requests.post(url, data=data, headers=header, proxies=ip).json()
            else:
                data = requests.post(url, data=data, headers=header).json()
            data = str(data)
            data = data.split('\'sort\': \'' + str(num) + '\'')[1]
            data = data.split('\', \'name\': \'')[1]
            data = data.split('\', \'category\'')[0]
            case = 2
            return data
        except:
            continue
def YesOrNot(ip,case='yes'):
    # 检测代理ip能否用于猎聘网的网页爬取中
    # ip:代理ip
    # 返回值:打印出代理ip和从服务器返回的值，如果返回值里面涵盖工作内容等信息，说明ip可以使用
    def get():
        jsdata = '''
        function r() {
        var e = 1 > 0 && void 0 !== 32 ? 32 : 32;
        console.assert(e >= 32, "最少需生成32位");
        var t = (new Date).getTime()
          , n = e < 32 ? 32 : e
          , r = new Array(n).join("x")
          , a = "".concat(r, "y").replace(/[xy]/g, (function(e) {
            var n = (t + 36 * Math.random()) % 36 | 0;
            return t = Math.floor(t / 36),
            ("x" == e ? n : 3 & n | 32).toString(36)
        }
        ));
        return a
    }'''
        sign = execjs.compile(jsdata).call('r')
        return sign
    def get_data(city, town, work, page, ip,townName):
        ckId_value = get()
        data = '{"data":{"mainSearchPcConditionForm":{"city":"' + str(city) + '","dq":"' + str(town) + '","pubTime":"","currentPage":"' + str(page) + '","pageSize":500,"key":"' + str(
            work) + '","suggestTag":"","workYearCode":"0","compId":"","compName":"","compTag":"","industry":"","salary":"","jobKind":"","compScale":"","compKind":"","compStage":"","eduLevel":"","otherCity":""},"passThroughForm":{"ckId":"' + str(
            ckId_value) + '","scene":"input","skId":"kidyjuir3x7rmen14hlz2kq1y9z6n3i3lqy","fkId":"kidyjuir3x7rmen14hlz2kq1y9z6n3i3lqy","sfrom":"search_job_pc"}}}'
        data = data.encode('utf-8')
        # print(data)
        header = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json;charset=utf-8;",
            "X-Client-Type": "web",
            "X-Fscp-Fe-Version": "",
            "X-Fscp-Version": "1.1",
            "X-Fscp-Std-Info": "{\"client_id\": \"40108\"}",
            "X-Fscp-Bi-Stat": "{\"location\": \"https://www.liepin.com/zhaopin/?city=410&dq=410&pubTime=&currentPage=0&pageSize=40&key=gs&suggestTag=&workYearCode=0&compId=&compName=&compTag=&industry=&salary=&jobKind=&compScale=&compKind=&compStage=&eduLevel=&otherCity=&sfrom=search_job_pc&scene=input&skId=xne9msayrzxkrk4njg7zq0ym8bfgoueb&fkId=xne9msayrzxkrk4njg7zq0ym8bfgoueb&ckId=" + str(
                ckId_value) + "&suggestId=\"}",
            "X-Requested-With": "XMLHttpRequest",
            "X-Fscp-Trace-Id": "7400ed8f-fa5d-46b3-ae30-c7b1189ded7c",
            "X-XSRF-TOKEN": "q4fNe47HRBup-djOx7S_0Q"
        }
        url = 'https://apic.liepin.com/api/com.liepin.searchfront4c.pc-search-job'
        if case=='yes':
            data = requests.post(url, data=data, headers=header,proxies=ip)
        else:
            data = requests.post(url, data=data, headers=header)
        res = data
        res.encoding = 'utf-8'
        res=res.json()
        print(ip,res)
    get_data('070030','070030010','数据',0,ip,'温州')
def CheckIp(ip):
    # ip:{'http': 'http://39.108.230.16:3128'}
    # 返回值:可以，不可以,返回值为文本
    try:
        if str(ip)[2:7] != 'https':
            res = requests.get('http://httpbin.org/ip', proxies=ip)
            result = '可以'
        else:
            res = requests.get('https://blog.sina.com.cn/', proxies=ip)
            result = '可以'
    except:
        result = '不行'
    return result
def IntoZip(dir_):
    # dir_:需要压缩的文件路径
    with ZipFile(str(dir_) + '.zip', 'w') as z:
        z.write(dir_, arcname=(dn := os.path.basename(dir_)))
        for root, dirs, files in os.walk(dir_):
            for fn in files:
                z.write(
                    fp := os.path.join(root, fn),
                    arcname=dn + '/' + os.path.relpath(fp, dir_)
                )
    print('压缩成功，已经压缩到了文件夹:' + str(dir_) + '.zip')
def ZipOut(dir, out):
    # dir:解压文件的路径，涵盖文件名
    # out:解压到
    zf = zipfile.ZipFile(dir)
    os.chdir(out)
    ret = zf.extractall(path=out)  # 解压到指定目录
    print('解压成功')
def SendEmail(name,password, receivers, text, sub, filepath):
    smtp_server = "smtp.qq.com"  # 发送邮箱服务器
    username = "yongxingkwok@foxmail.com"  # 用于发送邮箱的用户账号
    sender = 'yongxingkwok@foxmail.com'  # 发送者的邮箱
    EMAIL_FROM_NAME = name  # 自定义发件人名称
    time = datetime.datetime.today().strftime("%m-%d %H：%M")
    msg = MIMEMultipart()
    # 邮件正文
    msg.attach(MIMEText(str(text), 'plain', 'utf-8'))  # 文本内容换行\r\n
    msg['From'] = formataddr(pair=(EMAIL_FROM_NAME, sender))  # 自定义发件人的名称
    msg['To'] = ";".join(receivers)  # 发送给多个好友
    subject = str(sub).format(time)
    msg['Subject'] = subject
    if filepath != '':
        data = open(filepath, 'rb')
        ctype, encoding = mimetypes.guess_type(filepath)
        if ctype is None or encoding is not None:
            ctype = 'application/octet-stream'
        maintype, subtype = ctype.split('/', 1)
        file_msg = MIMEBase(maintype, subtype)
        file_msg.set_payload(data.read())
        data.close()
        encoders.encode_base64(file_msg)  # 把附件编码
        file_msg.add_header('Content-Disposition', 'attachment',
                            filename=str(filepath.split('\\')[-1].split('.')[0]))  # 修改邮件头
        msg.attach(file_msg)
    server = smtplib.SMTP(smtp_server)
    server.login(username, password)
    server.sendmail(sender, receivers, msg.as_string())
    server.quit()
def GetEmail(mail, password, dir):
    def decode_str(s):  # 字符编码转换
        value, charset = decode_header(s)[0]
        if charset:
            value = value.decode(charset)
            return value

    def get_email_title(msg):
        subject = email.header.decode_header(msg.get('subject'))
        if type(subject[-1][0]) == bytes:
            title = subject[-1][0].decode(str(subject[-1][1]))
        elif type(subject[-1][0]) == str:
            title = subject[-1][0]
        print("title:", title)
        return title

    def get_att(msg, dir):
        for part in msg.walk():
            # file_name = part.get_param("name")
            file_name = part.get_filename()
            if file_name:
                h = email.header.Header(file_name)
                dh = email.header.decode_header(h)
                filename = dh[0][0]
                if dh[0][1]:
                    filename = decode_str(str(filename, dh[0][1]))
                    data = part.get_payload(decode=True)
                    att_file = open(dir + file_name + '.zip', 'wb')
                    print('附件下载成功',file_name)
                    att_file.write(data)
                    att_file.close()

    """入口函数，登录imap服务"""
    server = imaplib.IMAP4_SSL('smtp.qq.com', 993)
    server.login(mail, password)
    server.select('INBOX')
    status, data = server.search(None, "ALL")
    if status != 'OK':
        raise Exception('read email error')
    emailids = data[0].split()
    mail_counts = len(emailids)
    # print("count:", mail_counts)
    # 邮件的遍历是按时间从后往前，这里我们选择最新的一封邮件
    for i in range(mail_counts - 1, mail_counts - 2, -2):
        status, edata = server.fetch(emailids[i], '(RFC822)')
        msg = email.message_from_bytes(edata[0][1])
        # 获取邮件主题title
        subject = email.header.decode_header(msg.get('subject'))
        if type(subject[-1][0]) == bytes:
            title = subject[-1][0].decode(str(subject[-1][1]))
        elif type(subject[-1][0]) == str:
            title = subject[-1][0]
        # print("title:", title)
        get_att(msg, dir)
def ProgressBar(i, sum, printvalue):
    sys.stdout.write('\r')
    sys.stdout.write('{}%|{}{}|{}'.format(int(i / sum * 100), ((int(i / sum * 100))) * '■',
                                          (100 - int(i / sum * 100 + 1)) * '_', '当前打印：' + str(printvalue)))
    sys.stdout.flush()
def MergeTable(data1, data2, on, data1name, data2name):
    data1 = pd.merge(data1, data2, on=on, how='outer')
    for i in range(0, len(list(data1))):
        data1 = data1.rename(
            columns={list(data1)[i]: list(data1)[i].replace('_x', data1name).replace('_y', data2name)})
    return data1
def ChoiceColumn(date,name):
    date1=date.copy()
    if len(name)==0:
        print(list(date))
    else:
        for i in range(0,len(list(date))):
            if list(date)[i] in name:
                pass
            else:
                del(date1[list(date)[i]])
    return date1
def PackageWithoutBorderBorder(file_path=r'python.py',ico_path='source\python.ico'):
    if os.path.exists(os.path.join(os.getcwd(),r'dist\python.exe')) is True:
        os.remove(os.path.join(os.getcwd(),r'dist\python.exe'))
    os.system('pyinstaller -F -w -i ' + os.path.join(os.getcwd(), ico_path) + ' ' + os.path.join(os.getcwd(), file_path))
def Package(file_path=r'python.py',ico_path='source\python.ico'):
    if os.path.exists(os.path.join(os.getcwd(),r'dist\python.exe')) is True:
        os.remove(os.path.join(os.getcwd(),r'dist\python.exe'))
    os.system('pyinstaller -F -i '+os.path.join(os.getcwd(),ico_path)+' '+os.path.join(os.getcwd(),file_path))
def DeleteAll():
    os.system('pip freeze>modules.txt')
    print('pip uninstall -r modules.txt -y')
def PackageService():
    if os.path.exists(os.path.join(os.getcwd(),r'dist\python.exe')) is True:
        os.remove(os.path.join(os.getcwd(),r'dist\python.exe'))
    code = 'pyinstaller -F -w --add-data="' + str(
        os.getcwd()) + '\\venv\Lib\site-packages\pyecharts;pyecharts"  --add-data="' + str(
        os.getcwd()) + '\\venv\Lib\site-packages\\flask;flask" --add-data=templates;templates --add-data=static;static -i ' + str(
        os.getcwd()) + '\\source\python.ico ' + str(os.getcwd()) + '\服务器后端.py'
    os.system(code)
def array_translation(date,num):
    # 数组平移函数，date表示需要平移的数组，num表示平移的个数
    date1=date[0:num]
    date2=date[num:len(date)]
    date=date2+date1
    return date
def work_path():
    name = str(os.getcwd())
    name = re.findall('.*\d*-[\u4e00-\u9fa5]*', name)
    os.chdir(name[0])
    import sys
    sys.path.append(os.getcwd())