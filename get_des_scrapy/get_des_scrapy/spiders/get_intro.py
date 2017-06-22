# -*- coding: utf-8 -*-

import re

import scrapy
import pymysql
from fake_useragent import UserAgent

from get_des_scrapy.items import IntroItem


class GetDesScrapySpider(scrapy.Spider):
	name = 'get_intro'
	start_url = 'https://www.baidu.com/s?q1=&q2=%s&q3=&q4=&gpc=stf&ft=&q5=1&q6=&tn=baiduadv'

	def __init__(self):
		# self.conn = pymysql.connect(host='127.0.0.1', user='root', passwd='3646287', db='spiders', charset="utf8", use_unicode=True)
		# self.conn = pymysql.connect(host='101.200.166.12', user='spider', passwd='spider', db='spider', charset="utf8", use_unicode=True)
		self.conn = pymysql.connect(host='10.44.60.141', user='spider', passwd='spider', db='spider', charset="utf8", use_unicode=True)
		self.cursor = self.conn.cursor()
		self.ua = UserAgent()

	def start_requests(self):
		select_sql = """select id, quan_cheng from tyc_jichu_bj where id < 200000"""
		self.cursor.execute(select_sql)
		results = self.cursor.fetchall() #元组包含元组或者空元组

		headers = {
			'Host': 'www.baidu.com',
			'User-Agent': self.ua.random,
		}
		for result in results:
			intro_item = IntroItem()
			id = result[0]
			quan_cheng = result[1]
			intro_item['id'] = id
			intro_item['quan_cheng'] = quan_cheng
			url = self.start_url % quan_cheng
			yield scrapy.Request(url, headers=headers, callback=self.parse, meta={'intro_item': intro_item})

	def parse(self, response):
		'''
		获取首页site并请求
		逻辑：获取百度搜索首页10个页面的out_site和cache_url（少于10个），去表site_xpath中对比，
		有这个site则发起请求，没有则直接不请求；有可能获取不全，如果判断不出，则还是需要申请
		'''
		intro_item = response.meta['intro_item']
		headers = {
			'Host': 'cache.baiducontent.com',
			'Referer': 'https://www.baidu.com/s?q1=&q2=%E7%A6%8F%E5%BB%BA%E5%A4%A7%E6%96%B9%E7%9D%A1%E7%9C%A0%E7%A7%91%E6%8A%80%E8%82%A1%E4%BB%BD%E6%9C%89%E9%99%90%E5%85%AC%E5%8F%B8&q3=&q4=&gpc=stf&ft=&q5=1&q6=&tn=baiduadv',
			'User-Agent': self.ua.random,
		}
		cache_obj = response.xpath('//div[@class="f13"]//a[@class="m"]')
		cache_urls_other = cache_obj.xpath('./@href').extract()
		cache_urls = [cache_url for cache_url in cache_urls_other if 'cache.baiducontent' in cache_url]
		# 获得的是与cache_url同位置的out_urls
		out_urls = cache_obj.xpath('../a[@class="c-showurl"]//text()').extract()
		for (cache_url, out_url) in zip(cache_urls, out_urls):
			out_site_obj = re.search(r"\.([-\w]+)\.(com|cn|com\.cn|net|org|gov|edu|int|mil|biz|info|tv|pro|name|museum|coop|aero|CC|SH|ME|asia|kim|hk)", out_url)
			if out_site_obj:
				# 如果匹配出了这个out_site_obj，就去site_xpath中查询，不在则return，在则发出请求
				out_site = out_site_obj.group(1)
				site_sql = """select site from bd_intro_xpath where site = %s"""
				self.cursor.execute(site_sql, out_site)
				result = self.cursor.fetchone()
				if not result:
					continue
				yield scrapy.Request(cache_url, headers=headers, callback=self.parse_cache, meta={'intro_item': intro_item})
			else:
				# 没匹配出，则一定要发此cache_url
				yield scrapy.Request(cache_url, headers=headers, callback=self.parse_cache, meta={'intro_item': intro_item})

	def parse_cache(self, response):
		'''
		解析每个site
		'''
		intro_item = response.meta['intro_item']
		id = intro_item['id']

		# 获取site，如果每个站点都没有，则跳过这个company了
		url = response.xpath('//div[@id="bd_snap_note"]//a//@href|.//*[@id="bd_snap_txt"]/a//@href').extract_first(
			default='')
		if url == '':
			return
		# site_obj = re.search(r"^.*\/.*\.(.*)\.(com|cn|com\.cn|net|org|biz|edu|cc|uk|mil|gov)\/.*$", url)
		site_obj = re.search(r"\.([-\w]+)\.(com|cn|com\.cn|net|org|gov|edu|int|mil|biz|info|tv|pro|name|museum|coop|aero|CC|SH|ME|asia|kim|hk)", url)
		if not site_obj:
			# intro_item['dict'] = [str({'None': ''})]
			return
		site = site_obj.group(1)

		# 判断此site是否在bd_intro的site_list中，在则直接return，不在则后续操作
		site_sql = """select site_list from bd_intro_bj where id = %s"""
		self.cursor.execute(site_sql, id)
		result = self.cursor.fetchone()
		if result:
			if site in result[0]:
				return

		# 取出此site的xpath，mysql中有此site的xpath，但是没有取到会跳过此site
		xpath_sql = """select xpath from bd_intro_xpath where site = %s"""
		self.cursor.execute(xpath_sql, site)
		result = self.cursor.fetchone()
		if not result:
			return
		xpath = result[0]

		# 获取公司简介
		intros = response.xpath(xpath).extract()
		if intros is None:
			return
		intro = "".join([x.strip() for x in intros])
		if intro == "":
			return

		intro_item['site_list'] = [site]
		intro_item['dict'] = [str({url: intro})]

		return intro_item
