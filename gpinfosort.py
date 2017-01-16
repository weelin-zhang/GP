# _*_ coding:utf-8 _*_

import requests,re,json,time,os
import heapq
from bs4 import BeautifulSoup

def item_in_a_and_b(a,b):
    temp_l = []
    for itema in a:
        for itemb in b:
            if itema[1]==itemb[1]:
                itema.append(itemb[2])
                temp_l.append(itema)
    return temp_l


class GPINFO(object):
    """docstring for GPINFO"""
    def __init__(self):
        self.Url = 'http://quote.eastmoney.com/stocklist.html'
        self.BaseData = []
        self.Date = time.strftime('%Y%m%d')
        self.Record = 'basedata'+self.Date
        if os.path.exists(self.Record):
            print ('record exist...')
            self.BaseData = self.get_base_data_from_record()
        else:
            print ('fuck-get data again...')
            self.get_data()

    def write_record(self,text):
        with open(self.Record,'ab') as f:
            f.write((text+'\n').encode('utf-8'))

    def get_base_data_from_record(self):
        ll = []
        with open(self.Record,'rb') as f:
            json_l = f.readlines()
            for j in json_l:
                ll.append(json.loads(j.decode('utf-8')))
        return ll

    def get_data(self):
        #请求数据
        orihtml = requests.get(self.Url).content
        #创建 beautifulsoup 对象
        soup = BeautifulSoup(orihtml,'lxml')
        #采集每一个股票的信息
        count = 0
        for a in soup.find('div',class_='quotebody').find_all('a',{'target':'_blank'}):
            record_d = {}
            #代号
            num = a.get_text().split('(')[1].strip(')')
            if not (num.startswith('00') or num.startswith('60')):continue #只需要6*/0*
            record_d['num']=num
            #名称
            name = a.get_text().split('(')[0]
            record_d['name']=name
            #详情页
            detail_url = a['href']
            record_d['detail_url']=detail_url

            cwzburl = detail_url
            #发送请求
            try:
                cwzbhtml = requests.get(cwzburl,timeout=30).content
            except Exception as e:
                print ('perhaps timeout:',e)
                continue
            #创建soup对象
            cwzbsoup = BeautifulSoup(cwzbhtml,'lxml')

            #财务指标列表 [浦发银行，总市值	净资产	净利润	市盈率	市净率	毛利率	净利率	ROE] roe:净资产收益率
            try:
                cwzb_list = cwzbsoup.find('div',class_='cwzb').tbody.tr.get_text().split()
            except Exception as e:
                print ('error:',e)
                continue
            #去除退市股票
            if '-' not in cwzb_list:
                record_d['data']=cwzb_list
                self.BaseData.append(record_d)
                self.write_record(json.dumps(record_d))
                count=count+1
                print (len(self.BaseData))

def main():
    test = GPINFO()
    result = test.BaseData
    #[浦发银行，总市值	净资产	净利润	市盈率	市净率	毛利率	净利率	ROE] roe:净资产收益率]
    top_10 = heapq.nlargest(10,result,key=lambda r:float(r['data'][7].strip('%')))
    for i in top_10:
        print(i['data'])

if __name__ == '__main__':
    main()




