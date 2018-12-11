import unittest
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import sqlite3 as sql
import sys
import os
import time

import db_main as db

cac = 'unitest_cache.json'
info = 'unitest_info.json'
gi = db.crawl_top_games(num=1,cache_file=cac,info_dict_file=info)

class TestWebscraping(unittest.TestCase):

    # def setUp(self):
    #     self.cac = 'unitest_cache.json'
    #     self.info = 'unitest_info.json'
    #     self.gi = db.crawl_top_games(num=1,cache_file=self.cac,info_dict_file=self.info)

    def tearDown(self):
        # Delete files created
        pass

    def testCacheExists(self):
        self.assertTrue(os.path.isfile(cac))

    def testGrabFromCache(self):
        t0 = time.time()
        db.crawl_top_games(num=1,cache_file=cac,info_dict_file=info)
        t1 = time.time()

        self.assertTrue((t1-t0) < 5.0)

    def testInfoFileExists(self):
        self.assertTrue(os.path.isfile(info))


    def testTitleInInfo(self):
        self.assertEqual(gi['games'][0]['title'],'Gloomhaven')

    def testCorrect_Entries_In_Info_Dict(self):
        self.assertEqual(len(gi['games']),1)
        self.assertEqual(len(gi['tp']),1)
        self.assertEqual(len(gi['td']),1)
        self.assertEqual(len(gi['tm']),9)



class TestDatabase:
    pass





class TestApp:
    pass

unittest.main(verbosity=2)
