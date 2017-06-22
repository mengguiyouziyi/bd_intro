# -*- coding: utf-8 -*-

import re

import scrapy
import pymysql

from get_des_scrapy.items import SiteXpathItem


# from selenium import webdriver
# from scrapy.xlib.pydispatch import dispatcher
# from scrapy import signals


class GetDesScrapySpider(scrapy.Spider):
	name = 'get_xpath'
	start_url = 'https://www.baidu.com/s?q1=&q2=%s&q3=&q4=&gpc=stf&ft=&q5=1&q6=&tn=baiduadv'

	# def __init__(self):
	#     self.browser = webdriver.Chrome(executable_path='/Users/menggui/Downloads/chromedriver')
	#     super(LagouSpider, self).__init__()
	#     dispatcher.connect(self.spider_closed, signals.spider_closed)
	#
	# def spider_closed(self, spider):
	#     print("spider closed")
	#     self.browser.quit()

	def __init__(self):
		# self.conn = pymysql.connect(host='127.0.0.1', user='root', passwd='3646287', db='spiders', charset="utf8", use_unicode=True)
		self.conn = pymysql.connect(host='101.200.166.12', user='spider', passwd='spider', db='spider', charset="utf8", use_unicode=True)
		self.cursor = self.conn.cursor()

	def start_requests(self):
		select_sql = """select id, quan_cheng from tyc_jichu_bj where id >= 110 and id < 150"""
		self.cursor.execute(select_sql)
		results = self.cursor.fetchall()  # 元组包含元组或者空元组

		headers = {
			'Host': 'www.baidu.com',
			'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:53.0) Gecko/20100101 Firefox/53.0',
		}
		for result in results:
			quan_cheng = result[1]
			url = self.start_url % quan_cheng
			yield scrapy.Request(url, headers=headers)

	def parse(self, response):
		'''
		获取首页site并请求
		'''
		headers = {
			'Host': 'cache.baiducontent.com',
			'Referer': 'https://www.baidu.com/s?q1=&q2=%E7%A6%8F%E5%BB%BA%E5%A4%A7%E6%96%B9%E7%9D%A1%E7%9C%A0%E7%A7%91%E6%8A%80%E8%82%A1%E4%BB%BD%E6%9C%89%E9%99%90%E5%85%AC%E5%8F%B8&q3=&q4=&gpc=stf&ft=&q5=1&q6=&tn=baiduadv',
			'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:53.0) Gecko/20100101 Firefox/53.0',
		}
		cache_urls = response.xpath('//a[@class="m"]//@href').extract()
		for cache_url in cache_urls:
			yield scrapy.Request(cache_url, headers=headers, callback=self.parse_cache)

	def parse_cache(self, response):
		'''
		解析每个site
		'''
		item = SiteXpathItem()
		url = response.xpath('//div[@id="bd_snap_note"]//a//@href|.//*[@id="bd_snap_txt"]/a//@href').extract_first(
			default='')
		site_obj = re.search(r'\.([-\w]+)\.(com|cn|com\.cn|net|org|gov|edu|int|mil|biz|info|tv|pro|name|museum|coop|aero|CC|SH|ME|asia|kim|hk)', url)
		if not site_obj:
			return
		site = site_obj.group(1)
		cache_url = response.url
		comp = re.compile(r'公司简介|公司介绍|公司说明|公司信息|企业简介|企业介绍|企业说明|企业信息|机构简介|机构介绍|机构说明|机构信息')
		intro_re = re.search(comp, response.text)
		if not intro_re:
			# 不包含简介，跳过
			self.logger.warn('no intro\nresponse网站为:%s\n' % response.url)
			return
		# 包含公司简介，则让用户打开网站，编辑xpath并输入
		self.logger.warn('have intro:%s\nresponse网站为:%s' % (intro_re.group(), response.url))
		# self.browser.get(response.request.url)
		xpath = input('请输入xpath：\n')
		if xpath == None or xpath == '':
			return
		xpath = xpath + '//text()'
		item['site'] = site
		item['url'] = url
		item['cache_url'] = cache_url
		item['xpath'] = xpath

		return item
