# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class FSpiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class CompanyListItem(scrapy.Item):
    name = scrapy.Field()
    c_id = scrapy.Field()


class CompanyInfoItem(scrapy.Item):
    """
    this item is company info which only get newest
    """
    c_name = scrapy.Field()  # 公司名称
    c_id = scrapy.Field()  # 公司股票id
    c_type = scrapy.Field()  # 机构类型
    c_des = scrapy.Field()  # 公司简介
    c_up_date = scrapy.Field()  # 上市时间
    c_addr = scrapy.Field()  # 公司地址
    c_net_addr = scrapy.Field()  # 公司网址
    c_e_name = scrapy.Field()  # 公司英文名称


class CompanyStockStructItem(scrapy.Item):
    """
    this item is stock struct which only get newest info about c_id company
    """
    c_id = scrapy.Field()
    s_struct = scrapy.Field()  # this is json like [['id','name','num','%','type]...]


class CompanyLeaderItem(scrapy.Item):
    """
    this item is company leader
    """
    c_id = scrapy.Field()
    leaders_list = scrapy.Field()  # this is json like [[['name', type, time, end_time]]]
