# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class SiteXpathItem(scrapy.Item):
    '''
    逻辑：一个site-xpath表，一张company-site表，site作为外键联系两张表。
    公司1 首页有10个site快照，其中三个有简介。
        两个程序：一个程序专门存储site-xpath（requests），另一个真正的抓取desc（scrapy）
    第一个程序：先给一批训练公司，循环查询首页，获取site，判断其中有无简介，若判断有简介，则通知用户打开网站，
            分析出并输入xpath，等程序获取并将xpath存入site-xpath表；
    第二个程序：循环查询公司，获取首页所有site站点，循环查询site-xpath中是否有此site，有则取出xpath解析获取desc，
            存入company-site表，如果循环完了首页所有site仍没有，则将此公司抛给第一个程序，进行下个公司的查询，
            并且将此公司记录下来。
    注意：
        第一个程序需单线程，1、便于与用户交互，2、当用户取xpath时阻塞，3、当训练数据用完时阻塞；
        第二个程序scrapy，1、

         公司2 首页有9个site快照，其中四个有简介，

    '''
    # company = scrapy.Field()# 搜索的公司名
    site = scrapy.Field() #站点
    url = scrapy.Field()  #原站点url
    cache_url = scrapy.Field() #快照url
    xpath = scrapy.Field() #配置的xpath


class IntroItem(scrapy.Item):
    id = scrapy.Field()
    quan_cheng = scrapy.Field()# 搜索的公司名
    site_list = scrapy.Field()# 搜索的公司名
    dict = scrapy.Field()