import requests
import json
from bs4 import BeautifulSoup
import time
import sqlite3
import random
import collections

def get_coord(geo):   #高德API 获取地理位置 景点位置
    result = {}
    loc = 0
    url = 'https://restapi.amap.com/v3/geocode/geo'  # 高德API
    params = {'key': '3e006793b8f4b0e2fd8da7af43b63b6c',
              'address': geo,
              }
    try:
        res = requests.get(url, params)
        answer = res.json()
        loc = answer['geocodes'][0]
        loc1 = loc['location']
        result[geo] = loc1
        return loc1

    except:
        result[geo] = None
        return None

def get_dis(loc1,loc2):        #高德api获取 两点间行程
    url = 'http://restapi.amap.com/v3/distance'
    params = {'key': '3e006793b8f4b0e2fd8da7af43b63b6c',
          'origins': loc1,
          'destination': loc2,
          'type': 1
             }
    res = requests.get(url, params)
    jd = json.loads(res.text)
    distance = jd['results'][0]['distance']
    return distance

def get_urls(city, page, url):  # https://you.ctrip.com/sight/guilin28/s0-p for all except hotel 获取景点
    urls = []
    for i in range(1, page + 1):
        urls.append(url + str(i) + '.html')
    return urls


def parse(urls, city):   #解析网页
    header = {
        'content-encoding': 'gzip',
        'sever': 'nginx/1.14.1',
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.52 Safari/536.5"
    }
    for url in urls:
        # print(response.text)
        response = requests.get(url, headers=header)
        soup = BeautifulSoup(response.text, 'html.parser')
        list_sights = soup.find_all('div', {'class': 'list_mod2'})  # get all sights

        for sight in list_sights:  # for single sight
            sight = sight.find('div', {'class': 'rdetailbox'})
            name = sight.find('a', {'target': '_blank'}).string.split()[0]
            address = sight.find('dd', {'class': 'ellipsis'}).string.split()[0]
            try:
                rating = sight.find('strong').string
                float(rating)
            except:
                rating = '3.5'
            try:
                price = sight.find('span', {'class': 'price'}).text[1::]
            except:
                price = '20'
            hotel_price = str(get_hotel(city, name))
            time.sleep(3)
            cord1 = get_coord(address)
            dis_price = get_dis(cord1, dic_dis[city])
            print('城市:' + city + '  景点:' + name + '  评分:' + rating + '  景点价格:' + price + '  旅馆价格:' + hotel_price + '  行程距离(米):' + dis_price + ' 景点地址:' + address)

            dict_sight[city][name] = [address, rating, price, hotel_price, dis_price]  # record down,travel_price

        # print(len(list_sights))
        time.sleep(5)

def get_hotel(city,sight):   #获取酒店价格
    if city == '丽江市':
        url = 'http://hotel.elong.com/search/list_cn_2503.html?keywords='
    elif city == '成都市':
        url = 'http://hotel.elong.com/search/list_cn_2301.html?keywords='
    else:
        url = 'http://hotel.elong.com/search/list_cn_2601.html?keywords='
    header = {
        'content-encoding':'gzip',
        'sever':'nginx/1.14.1',
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.52 Safari/536.5"
    }
    try:
        response = requests.get(url+sight,headers = header,timeout = 15)
        soup = BeautifulSoup(response.text, "html.parser")
    except:
        return round(float(random.randint(200,450)),1)
    try:
        prices = soup.find_all('span',{'class':'h_pri_num'})
        return sum(list(map(lambda i:int(i.string),prices)))/len(prices)
    except:
        return round(float(random.randint(200,450)),1)

def main():    #程序入口
    targets = ['丽江市','成都市','拉萨市']
    page = {'丽江市':2 ,'成都市':2,'拉萨市':2 }#{'丽江市':16 ,'成都市':40,'拉萨市':11}
    urls = {'丽江市':'https://you.ctrip.com/sight/lijiang32/s0-p' ,'成都市':'https://you.ctrip.com/sight/chengdu104/s0-p','拉萨市':'https://you.ctrip.com/sight/lhasa36/s0-p'}
    for city in targets:
        url = get_urls(city ,page[city],urls[city])
        parse(url,city)

def creat():   #创建sql
    cx = sqlite3.connect("test.db")
    c = cx.cursor()
    try:
        c.execute('''create table lijiang(sight text, overal real,rating real, sight_price real, hotel_price real,distance_price real, sight_address text)''')
        c.execute('''create table chengdu(sight text, overal real, rating real, sight_price real, hotel_price real,distance_price real, sight_address text)''')
        c.execute('''create table lasa(sight text,overal real, rating real, sight_price real, hotel_price real,distance_price real, sight_address text)''')
        cx.commit()
    except:
        print('table already exist')
        return False
    c.close()
    cx.close()
    return True

def insert():  #插入sql数据
    cx = sqlite3.connect("test.db")
    c = cx.cursor()
    dic_all = collections.defaultdict(list)
    for i in dict_sight.keys():
        for j in dict_sight[i].keys():
            dic_all[i].append([j,float(dict_sight[i][j][1])/(float(dict_sight[i][j][2])*float(dict_sight[i][j][3])*float(dict_sight[i][j][4])),dict_sight[i][j][1],dict_sight[i][j][2],dict_sight[i][j][3],dict_sight[i][j][4],dict_sight[i][j][0]])
    for i in dic_all:
        dic_all[i].sort(key=lambda j: j[1], reverse=True)

    for i in dic_all:
        n = len(dic_all[i])
        for j in range(n):
            if j <= n*0.4: dic_all[i][j][1] = 3
            elif n*0.4 < j <= n*0.5: dic_all[i][j][1] = 2
            elif n*0.5 < j <= n*0.6: dic_all[i][j][1] = 1
            else:
                dic_all[i][j][1] = 0
    for i in dic_all.keys():
        for j in dic_all[i]:
            info = tuple(j)
            if i == '丽江市':
                c.execute("insert into lijiang (sight, overal,rating, sight_price, hotel_price,distance_price, sight_address) values(?, ?,?,?,?,?,?)", info)
            elif i == '成都市':
                c.execute("insert into chengdu (sight, overal,rating, sight_price, hotel_price,distance_price, sight_address) values(?, ?,?,?,?,?,?)", info)
            else:
                c.execute("insert into lasa (sight, overal,rating, sight_price, hotel_price,distance_price, sight_address) values(?, ?,?,?,?,?,?)", info)
    cx.commit()
    c.close()
    cx.close()

def get_all():   #暂时没用 debug用
    cx = sqlite3.connect("test.db")
    c = cx.cursor()
    c.execute('SELECT * FROM lijiang')
    rows = c.fetchall()
    for row in rows:
        print(row)
    cx.commit()
    c.close()
    cx.close()

dict_sight = {'丽江市': dict(), '成都市': dict(), '拉萨市': dict()}
dic_dis = {'丽江市': '100.226650,26.854841', '成都市': '104.041016,30.690389', '拉萨市': '91.171961,29.653482'}   # 各个城市的地点
main()
print('start writing data to sql database')
boolean = creat()
if boolean:
    insert()
print('please open http://127.0.0.1:5000/login to login')
exec(open('app.py').read())   #打卡端口




"""
def result():
    print('丽江市景点排名： （景点， 综合得分， 携程景点评分，景点价格，旅馆价格，路程距离，地址 ）')
    n = len(lst1)
    count = 0
    lst1.sort(key = lambda j:j[1],reverse = True)
    for i in lst1:
        if count <= n*0.4: score = 3
        elif n*0.4 < count <= n*0.5: score = 2
        elif n*0.5 < count <= n*0.6: score = 1
        else:
            score = 0
        #tplt = "{0:{3}^15}\t{1:{3}^10}\t{2:^10}"
        print(str(i[0]).ljust(20)+str(score).ljust(6)+str(i[2]).ljust(6)+str(i[3]).ljust(12)+str(i[4]).ljust(12)+str(i[5]).ljust(12)+str(i[6]).ljust(20))
        count += 1
    print('------------------------------------------------------------------------------------------')
    print('成都市景点排名： （景点， 综合得分， 携程景点评分，景点价格，旅馆价格，路程距离，地址 ）')
    lst2.sort(key=lambda j: j[1], reverse=True)
    n = len(lst2)
    count = 0
    for i in lst2:
        if count <= n*0.4: score = 3
        elif n*0.4 < count <= n*0.5: score = 2
        elif n*0.5 < count <= n*0.6: score = 1
        else:
            score = 0
        print(str(i[0]).ljust(20)+str(score).ljust(6)+str(i[2]).ljust(6)+str(i[3]).ljust(6)+str(i[4]).ljust(6)+str(i[5]).ljust(6)+str(i[6]).ljust(20))
        count += 1
    print('------------------------------------------------------------------------------------------')
    print('拉萨市景点排名： （景点， 综合得分， 携程景点评分，景点价格，旅馆价格，路程距离，地址 ）')
    n = len(lst3)
    count = 0
    lst3.sort(key=lambda j: j[1], reverse=True)
    for i in lst3:
        if count <= n*0.4: score = 3
        elif n*0.4 < count <= n*0.5: score = 2
        elif n*0.5 < count <= n*0.6: score = 1
        else:
            score = 0
        print(str(i[0]).ljust(20)+str(score).ljust(6)+str(i[2]).ljust(6)+str(i[3]).ljust(6)+str(i[4]).ljust(6)+str(i[5]).ljust(6)+str(i[6]).ljust(20))
        count += 1

result()
"""
