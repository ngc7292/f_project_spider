#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__title__ = ''
__author__ = 'ngc7293'
__mtime__ = '2020-04-08'
"""
import scrapy
import json
import time
import re

from bs4 import BeautifulSoup
from f_spider.items import CompanyStockStructItem, CompanyLeaderItem, CompanyInfoItem


def get_time(time_s):
    """
    this function is from time stirng to timestmp
    :param time_s: year-mouth-day
    :return: timestamp
    """
    return time.mktime(time.strptime(time_s, "%Y-%m-%d"))


def clean_s(s):
    clean_list = [" ", "\n", "\r", "\t", "\xa0", "："]
    for i in clean_list:
        s = s.replace(i, "")
    return s


class ShCompanySpidar(scrapy.Spider):
    """
    this scpidar is for shenzhen ee company list
    """
    name = "szcompanys"
    allowed_domains = ['sina.com.cn', 'szse.cn']
    
    def start_requests(self):
        start_url = "http://www.szse.cn/api/report/ShowReport/data?SHOWTYPE=JSON&CATALOGID=1110&loading=first"
        yield scrapy.Request(url=start_url, callback=self.page_count_parse)
    
    def page_count_parse(self, response):
        body = response.body
        try:
            page_count = json.loads(body)[0]['metadata']['pagecount']
            self.log("page count is "+str(page_count))
            page_url = "http://www.szse.cn/api/report/ShowReport/data?SHOWTYPE=JSON&CATALOGID=1110&TABKEY=tab1&PAGENO" \
                       "={id}"
            for p_id in range(page_count):
                yield scrapy.Request(url=page_url.format(id=p_id), callback=self.company_list_parse)
        except:
            self.error("something error in get list!")
    
    def company_list_parse(self, response):
        body = response.body
        try:
            company_list = json.loads(body)[0]['data']
            self.log("get company "+str(len(company_list))+".")
            for company in company_list:
                company_id = company['zqdm']
                
                stock_url = "http://vip.stock.finance.sina.com.cn/corp/go.php/vCI_CirculateStockHolder/stockid/{s_id}/displaytype/30.phtml".format(
                    s_id=company_id)
                
                leader_url = "https://vip.stock.finance.sina.com.cn/corp/go.php/vCI_CorpManager/stockid/{c_id}.phtml".format(
                    c_id=company_id)
                
                info_url = "https://vip.stock.finance.sina.com.cn/corp/go.php/vCI_CorpInfo/stockid/{c_id}.phtml".format(
                    c_id=company_id)
                
                headers = {
                    'Cookie': 'U_TRS1=0000003c.88c435a7.5e8d25ad.d3032e5d; U_TRS2=0000003c.88d235a7.5e8d25ad.c19cf323',
                    'referer': 'None'}
                
                yield scrapy.Request(url=info_url, headers=headers, callback=self.get_company_info_parse)
                yield scrapy.Request(url=stock_url, headers=headers, callback=self.get_stock_struct_parse)
                yield scrapy.Request(url=leader_url, headers=headers, callback=self.get_company_leaders_parse)
        except:
            self.log("error in get company list")
    
    def get_stock_struct_parse(self, response):
        item = CompanyStockStructItem()
        r_data = BeautifulSoup(response.body.decode('gbk'), features="lxml")
        r_data = r_data.find(id="CirculateShareholderTable")
        res = []
        for tr in r_data.find_all("tr"):
            tr_list = []
            for td in tr.find_all("td"):
                s = td.string
                
                tr_list.append(s)
            if len(tr_list) == 5 and str.isdigit(tr_list[0]):
                res.append(tr_list)
        
        item['c_id'] = response.url.split("/")[-3]
        item['s_struct'] = json.dumps(res)
        # print(res)
        yield item
    
    def get_company_leaders_parse(self, response):
        item = CompanyLeaderItem()
        r_data = response.body.decode("gbk")
        r_data = BeautifulSoup(r_data, features='lxml')
        r_data = r_data.find_all("table", id='comInfo1')
        res = []
        for table in r_data:
            t_list = []
            for tr in table.find_all("tr"):
                tr_list = []
                for td in tr.find_all("td"):
                    if td.a != None:
                        std = td.a.string
                    else:
                        std = td.string
                    tr_list.append(std)
                if len(tr_list) == 0 or len(tr_list) == 1 or tr_list[0] == "姓 名":
                    continue
                else:
                    t_list.append(tr_list)
            res+=t_list
        item['c_id'] = response.url.split("/")[-1].split(".")[0]
        item['leaders_list'] = json.dumps(res)
        # print(res)
        yield item
    
    def get_company_info_parse(self, response):
        item = CompanyInfoItem()
        r_data = BeautifulSoup(response.body.decode('gbk'), features='lxml')
        r_data = r_data.find("table", id='comInfo1')
        res = []
        
        for tr in r_data.find_all("tr"):
            tr_list = []
            for td in tr.find_all("td"):
                s = td.get_text()
                s = clean_s(s)
                tr_list.append(s)
            
            res += tr_list
        # print(res)
        q_dict = {"公司名称": "c_name", "机构类型": "c_type", "公司简介": "c_des", "上市日期": "c_up_date", "注册地址": "c_addr",
                  "公司网址": "c_net_addr", "公司英文名称": "c_e_name"}
        
        for i in range(len(res)):
            if q_dict.get(res[i]) != None:
                item[q_dict[res[i]]] = res[i + 1]
        item['c_id'] = response.url.split("/")[-1].split(".")[0]
        yield item
