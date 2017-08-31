# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import json
import pymysql


class JsonWriterPipeline(object):
	def __init__(self):
		self.file = open('items.json', 'w')

	def process_item(self, item, spider):
		line = json.dumps(dict(item), ensure_ascii=False) + "\n"
		self.file.write(line)
		return item

	def spider_closed(self, spider):
		self.file.close()


class MysqlPipeline(object):
	"""
	需要考虑：
	1、有时候明明没有'公司简介'等，或者有，但是没有具体内容，xpath怎么定义才合法
	2、当一条xpath取出的简介内容为空字符串时，判断字符串长度或者判断是否为空，就是说并非没有此xpath，只是取出为空
	"""

	# def __init__(self):
		# self.conn1 = pymysql.connect(host='etl2.innotree.org', port=3308, user='spider', passwd='spider', db='spider',
		#                              charset="utf8", use_unicode=True)
		# self.cursor1 = self.conn1.cursor()

	def process_item(self, item, spider):
		if spider.name == 'get_xpath':
			# 进了此处的item就有xpath，获取的应该是元组
			path = path_from_item = item['xpath']

			select_sql = """select xpath from bd_intro_xpath where site = %s"""
			spider.cursor.execute(select_sql, item['site'])
			result = spider.cursor.fetchone()
			if result is not None:
				# 如果有此site，从数据库中获取的xpath
				xpath_from_db = result[0]
				path = xpath_from_db + ('|' + path_from_item)

			# 无论数据库有无此site
			xpath_sql = """replace into bd_intro_xpath(site, url, cache_url, xpath) VALUES (%s, %s, %s, %s)"""
			spider.cursor.execute(xpath_sql, (item["site"], item["url"], item["cache_url"], path))
			spider.conn.commit()
		elif spider.name == 'get_intro':
			# 进了此处的item就有xpath，获取的应该是元组

			site_list = site_list_from_item = item['site_list']
			site_list_sel_sql = """select site_list from bd_intro_bj_copy where id = %s"""
			spider.cursor1.execute(site_list_sel_sql, item["id"])
			result = spider.cursor1.fetchone()
			if result is not None:
				# 如果有此id，从数据库中获取intro，tuple类型
				# ["['jobui', '11467']", '11467']
				site_list = list(result)
				site_list.append(site_list_from_item[0])
				site_list = ','.join(site_list)

			dict = dict_from_item = item['dict']
			dict_sel_sql = """select dict from bd_intro_bj_copy where id = %s"""
			spider.cursor1.execute(dict_sel_sql, item["id"])
			result = spider.cursor1.fetchone()
			if result is not None:
				# 如果有此id，从数据库中获取intro，tuple类型
				dict = list(result)
				dict.append(dict_from_item[0])
				dict = ','.join(dict)

			intro_sql = """replace into bd_intro_bj_copy (id, quan_cheng, site_list, dict) values (%s, %s, %s, %s)"""
			args = (item["id"], item["quan_cheng"], site_list, dict)
			spider.cursor1.execute(intro_sql, args)
			spider.conn1.commit()
			# print(item["quan_cheng"])

		return item
