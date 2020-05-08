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

