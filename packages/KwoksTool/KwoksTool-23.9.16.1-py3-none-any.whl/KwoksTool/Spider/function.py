def find_diffrent_key_from_str(date1,date2):
    # 调用此函数可以快速对比两列字符串，查找出key值不一样的值，用于在数据爬取过程中快速对比并查找出需要破解的参数
    def change_txt_to_list(info_list):
        info_list=info_list.split('&')
        result={}
        for i in range(len(info_list)):
            info=info_list[i].split('=')
            result[info[0]]=info[1]
        return  result
    date1=change_txt_to_list(date1)
    date2=change_txt_to_list(date2)
    for son in date2.keys():
        if date1[son]!=date2[son]:
            print(son+':\n  (1)'+date1[son]+'\n  (2)'+date2[son])