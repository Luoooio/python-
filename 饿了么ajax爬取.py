# -*- coding: utf-8 -*-
"""
Created on Wed Nov 21 11:52:31 2018

@author: luodashi
"""

from urllib.parse import urlencode
import requests
import pandas as pd
import numpy as np
import time
import base64
base_url = 'https://h5.ele.me/restapi/shopping/v3/restaurants?'  #请求url的前办部分
headers = {'Host':'h5.ele.me',
            'Referer':'https://h5.ele.me/',
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.92 Safari/537.36',
            
            }  #构造请求头

args_strs = '''latitude: 30.474852
longitude: 114.356769
limit: 8
extra_filters: home
rank_id: 545fa8893d324755831a6f0a15c4af9e
terminal: h5'''
last_list=[]
error_l = []
proxyHost = "http-dyn.abuyun.com"
proxyPort = "9020"
proxyUser = "H09F18IE2QY19J6D"
proxyPass = "88050C531F3FE8B4"
proxyMeta = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {
      "host" : proxyHost,
      "port" : proxyPort,
      "user" : proxyUser,
      "pass" : proxyPass,
    }
proxies = {
        "http"  : proxyMeta,
        "https" : proxyMeta,
    }
def args_strs_to_dict(args):  #将字符串转化为字典
    dicts = {}
    if '\n' in args:
        lists = args.split('\n')
        for i in lists:
            key = i.split(':')[0]
            value = i.split(':')[1]
            dicts[key]=value.strip()
    return dicts
def get_page(page):      #构造每一个下拉页面的url，并返回内容
    args_dict = args_strs_to_dict(args_strs)
    url = base_url+urlencode(args_dict)+'&offset='+str(page)+'&extras[]=activities&extras[]=tags'
    print(url)
    try:
        response = Session.get(url,headers=headers,proxies=proxies)
        if response.status_code == 200:
            return response.json()  
        else:
            print(response.json()['message'])
            return None
    except requests.ConnectionError as e:
        print('第'+str(page)+'Error',e.args)
        return None
def parse_page(json):   #对内容进行解析，将每一家店铺信息作为字典添加进列表
    if json:      
        items = json.get('items')
        print(len(items))
        for item  in items:
            alone = {}
            restaurant = item.get('restaurant')
            alone['店铺名称'] = restaurant.get('name')
            alone['地址'] = restaurant.get('address')
            alone['配送费'] = restaurant.get('float_delivery_fee')
            alone['起送价格'] = restaurant.get('float_minimum_order_amount')
            alone['评分'] = restaurant.get('rating')
            alone['平均送达时间'] = restaurant.get('order_lead_time')
            alone['月订单量'] = restaurant.get('recent_order_num')
            alone['距离'] = restaurant.get('distance')
            for i in restaurant.get('support_tags'):
                if i.get('text') == '品质联盟':
                    alone['品质联盟'] = '是'
                    break
                else:
                    alone['品质联盟'] = '否'
            if restaurant.get('delivery_mode') :
                alone['蜂鸟专送'] = '是'
            else:
                alone['蜂鸟专送'] = '否'
            for i in restaurant.get('support_tags'):
                if i.get('text') == '口碑人气好店':
                    alone['口碑人气好店'] = '是'
                    break
                else:
                    alone['口碑人气好店'] = '否'
            
            last_list.append(alone)

def session_l():  #获得登陆后的session
    session = requests.Session()
    url_code = 'https://h5.ele.me/restapi/eus/login/mobile_send_code'  #post请求验证码的网址
    url_verify = 'https://h5.ele.me/restapi/eus/v3/captchas'   #post请求图形验证码的网址
    url_login = 'https://h5.ele.me/restapi/eus/login/login_by_mobile'  #最终登陆界面
    data_code_easy = {'captcha_hash':'',
                          'captcha_value':'',
                          'mobile': "18781159162"}
    verify_data = {'captcha_str': "18781159162"}
    session_respond = session.post(url=url_code,data = data_code_easy,headers = headers)
    if session_respond.status_code == 400:
        session_verify_respond = session.post(url=url_verify,data = verify_data,headers = headers)  #拿到'captcha_hash、captcha_value参数构建对验证码的请求，完成图形验证
        hcaptcha_hash = session_verify_respond.json()['captcha_hash']  
        imgdata = base64.b64decode(session_verify_respond.json()['captcha_image'].split(',')[-1])
        with open(r'C:\Users\luodashi\Desktop\检验码.jpg','wb') as f:
            f.write(imgdata)
        captcha_value = input('请输入图形码：')
        data_code = {'captcha_hash': hcaptcha_hash,
                     'captcha_value': captcha_value,
                    'mobile': "18781159162"}
        session_respond_code = session.post(url=url_code,data = data_code,headers = headers)   #拿到validate_token参数，构建对登陆的请求
        validate_token = session_respond_code.json()['validate_token']
        validate_code = input('请输入验证码：')
        login_data = {'mobile': "18781159162",
                      'validate_code': validate_code,
                      'validate_token': validate_token}
        session_respond_login = session.post(url = url_login,data = login_data,headers = headers)
        return session
    elif session_respond.status_code ==200:
        validate_token = session_respond.json()['validate_token']
        validate_code = input('请输入验证码：')
        login_data = {'mobile': "18781159162",
                      'validate_code': validate_code,
                      'validate_token': validate_token}
        session_respond_login = session.post(url = url_login,data = login_data,headers = headers)
        return session
    else:
        print('session构建错误')
def main():
    i = 0
    while True:
        json = get_page(i*8)
        print('爬取第'+str(i)+'页数据完成')
        if json == None:
            print("第"+str(i)+'页错误')
            error_l.append(i)
            i+=1
            continue        #将出现请求错误的页码放入列表
        i +=1
        parse_page(json)
        time.sleep(0.5)
        if i==70:
            break  
def error_l_main():      #对错误页码再次爬取，直到列表为空
    for i in error_l:
        json = get_page(i*8)
        print('爬取第'+str(i)+'数据完成')
        if json == None:  
            continue
        parse_page(json)
        error_l.remove(i)   
Session = session_l()
main()
while error_l != []:
    error_l_main()
print(error_l)
df = pd.DataFrame(last_list)
df.to_excel(r'C:\Users\luodashi\Desktop\饿了么移动版数据爬取.xlsx')  #将字典列表转化为dataframe对象再保存为excel

