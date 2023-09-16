import json
def SelecTHead(html,dict):
    text_single = '''<div data-v-6e2a8889="" style="display: inline-block;position: relative;cursor: pointer;height: 3%;line-height: 23px;border: 1px solid #000000;color: #000000;background: #b8c0e0;padding: 0 8px;font-size: 12px;margin-left: 5px;margin-top: 4px" onclick="window.open('显示地址','_self')">显示名称<!----></div>'''
    text_sum = text_single.replace('显示名称', dict[0]['名称']).replace('显示地址', dict[0]['地址'])
    for i in range(1,len(dict)):
        text_single='''<div data-v-6e2a8889="" style="display: inline-block;position: relative;cursor: pointer;height: 3%;line-height: 23px;border: 1px solid #000000;color: #000000;background: #b8c0e0;padding: 0 8px;font-size: 12px;margin-left: 5px;margin-top: 4px" onclick="window.open('显示地址','_self')">显示名称<!----></div>'''
        text_sum=text_sum+text_single.replace('显示名称',dict[i]['名称']).replace('显示地址',dict[i]['地址'])
    text_sum='''<body style="background-color: #000649;">
    <style>.box {  } </style>        <!--=========================================-->
    <div class="box" style="background-color: #000649;width: 100%;height:100%">
        <!--=========================================-->
<div ">'''+text_sum+'''</div>
</div>
<!--=========================================-->'''
    with open(html, "r", encoding="utf8") as f:
        f=f.read()
    f=f.replace('''<body >
    <style>.box {  } </style>    <div class="box">''',text_sum)
    with open(html,'w',encoding='utf-8') as ff:
        ff=ff.write(f)
    return text_sum
def px_to_percent(path):
    # px_to_percent('F:\系统\桌面\chart_config.json', 923, 570)
    with open(path,encoding='utf-8') as f:
        f=f.read()
        f=json.loads(f)
    width=None
    height=None
    for i in range(len(f)):
        if f[i]['cid']=='image':
            width=float(f[i]['width'][:-2])
            height=float(f[i]['height'][:-2])
    if width is None or height is None:
        input('最大尺寸数据没有获取，请检查是否有image的尺寸')
    def get_int(date,sum):
        date=str(int(float(date[:-2])/sum*1000)/10)+'%'
        return date
    for i in range(len(f)):
        f[i]['width']=get_int(f[i]['width'],width)
        f[i]['left']=get_int(f[i]['left'],width)
        f[i]['height']=get_int(f[i]['height'],height)
        f[i]['top']=str(float(get_int(f[i]['top'],height)[:-1]))+'%'
    f=json.dumps(f)
    with open(path,'w',encoding='utf-8') as ff:
        ff.write(f)