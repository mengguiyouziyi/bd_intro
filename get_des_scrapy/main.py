# -*- coding: utf-8 -*-
__author__ = 'Sunny'

from scrapy.cmdline import execute

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# execute(["scrapy", "crawl", "get_xpath"])
execute(["scrapy", "crawl", "get_intro"])