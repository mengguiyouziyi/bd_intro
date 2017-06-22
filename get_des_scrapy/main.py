# -*- coding: utf-8 -*-
__author__ = 'Sunny'

import sys, os
from multiprocessing import Pool

from scrapy.cmdline import execute

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def main():
	# execute(["scrapy", "crawl", "get_xpath"])
	execute(["scrapy", "crawl", "get_intro"])


p = Pool(processes=3)
p.apply_async(main())
p.close()
p.join()
