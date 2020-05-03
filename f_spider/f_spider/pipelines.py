# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json

from .items import CompanyInfoItem, CompanyLeaderItem, CompanyStockStructItem
from py2neo import Graph, Node, Relationship


class FSpiderPipeline(object):
    def process_item(self, item, spider):
        print("test pipeline item")
        return item


class NeoPipeline(object):
    """
    this pipeline is save the data from spider to neo4j database
    """
    
    def __init__(self, url, username, password):
        self.url = url
        self.username = username
        self.password = password
    
    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            url=crawler.settings.get('NEO4J_URL'),
            username=crawler.settings.get('NEO4j_USERNAME'),
            password=crawler.settings.get('NEO4J_PASSWORD')
        )
    
    def open_spider(self, spider):
        self.graph = Graph(
            uri=self.url,
            usernmae=self.username,
            password=self.password
        )
        spider.log('neo4j pipeline is starting')
    
    def close_spider(self, spider):
        spider.log('neo4j pipeline is been closed')
    
    def process_item(self, item, spider):
        # print(type(item))
        if isinstance(item, CompanyLeaderItem):
            c_id = item['c_id']
            
            c_node = self.graph.nodes.match("Company", c_id=c_id).first()
            if c_node is None:
                c_node = self.create_Company(c_id)
            
            leaders_list = json.loads(item['leaders_list'])
            for leader in leaders_list:
                p_name = leader[0]
                s_type = leader[1]
                s_start_time = leader[2]
                s_end_time = leader[3]
                
                p_node = self.graph.nodes.match("Person", p_name=p_name).first()
                if p_node is None:
                    p_node = self.create_Person(p_name)
                
                serve_relation = self.create_serve(c_node, p_node, s_type, s_start_time, s_end_time)
        
        elif isinstance(item, CompanyStockStructItem):
            c_id = item['c_id']
            c_node = self.graph.nodes.match("Company", c_id=c_id).first()
            if c_node is None:
                c_node = self.create_Company(c_id)
            
            s_struct_list = json.loads(item['s_struct'])
            for s_struct in s_struct_list:
                s_id = s_struct[0]
                s_name = s_struct[1]
                h_total = s_struct[2]
                h_prop = s_struct[3]
                h_type = s_struct[4]
                
                sh_node = self.graph.nodes.match(s_name=s_name).first()
                if sh_node is None:
                    sh_node = self.create_ShareHolder(s_name)
                
                hold_relation = self.create_hold(c_node, sh_node, h_type, h_prop, h_total)
        elif isinstance(item, CompanyInfoItem):
            c_id = item['c_id']
            c_node = self.graph.nodes.match("Company", c_id=c_id).first()
            if c_node is None:
                c_node = self.create_Company(c_id, item)
            else:
                c_node = self.update_Company(c_node, item)
                
        return item['c_id']
    
    def create_Company(self, c_id, item = None):
        
        r_node = Node(
            "Company",
            c_id=c_id,
            c_name="",
            c_type="",
            c_des="",
            c_up_date="",
            c_addr="",
            c_net_addr="",
            c_e_name=""
        )
        
        self.graph.create(r_node)
        if item is not None:
            self.update_Company(r_node, item)
        return r_node
    
    def update_Company(self, r_node, item):
        r_node['c_name'] = item['c_name']
        r_node['c_type'] = item['c_type']
        r_node['c_des'] = item['c_des']
        r_node['c_up_date'] = item['c_up_date']
        r_node['c_addr'] = item['c_addr']
        r_node['c_net_addr'] = item['c_net_addr']
        r_node['c_e_name'] = item['c_e_name']
        
        self.graph.push(r_node)
        return r_node
    
    def create_ShareHolder(self, name):
        r_node = Node("ShareHolder", s_name=name)
        self.graph.create(r_node)
        return r_node
    
    def create_Person(self, name):
        r_node = Node("Person", p_name=name)
        self.graph.create(r_node)
        return r_node
    
    def create_hold(self, c_node, sh_node, h_type, h_prop, h_total):
        r_relation = Relationship(sh_node, "hold", c_node, h_type=h_type, h_prop=h_prop, h_total=h_total)
        self.graph.create(r_relation)
        return r_relation
    
    def create_serve(self, c_node, p_node, s_type, s_start_time, s_end_time):
        r_relation = Relationship(p_node, "serve", c_node, s_type=s_type, s_start_time=s_start_time,
                                  s_end_time=s_end_time)
        self.graph.create(r_relation)
        return r_relation
