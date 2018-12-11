# This is a set of unit tests for the final project.

import unittest
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import sqlite3 as sql
import sys
import os
import time

import db_main as db
import app_model as am

class TestWebscraping(unittest.TestCase):

    def testCacheExists(self):
        self.assertTrue(os.path.isfile(cac))

    def testGrabFromCache(self):
        t0 = time.time()
        db.crawl_top_games(num=1,cache_file=cac,info_dict_file=info)
        t1 = time.time()

        self.assertTrue((t1-t0) < 15.0)

    def testInfoFileExists(self):
        self.assertTrue(os.path.isfile(info))


    def testTitleInInfo(self):
        self.assertEqual(gi['games'][0]['title'],'Gloomhaven')

    def testCorrect_Entries_In_Info_Dict(self):
        self.assertEqual(len(gi['games']),1)
        self.assertEqual(len(gi['tp']),1)
        self.assertEqual(len(gi['td']),1)
        self.assertEqual(len(gi['tm']),9)

# unittest.main(verbosity=2)

class TestDatabase(unittest.TestCase):

# def setUp(self,dbname='unittest.db'):
#     self.conn = sql.connect(dbname)
#     self.cur = conn.cursor()
#
# def tearDown(self):
#     self.conn.close()

    def testDB_Generation(self):
        db.initialize_db(DB_FILE='unittest.db')
        self.assertTrue(os.path.isfile('unittest.db'))

    def testDB_Population(self):
        db.populate_db(info,'unittest.db')
        conn = sql.connect('unittest.db')
        cur = conn.cursor()
        statement = '''SELECT Title FROM Game'''
        cur.execute(statement)
        out = []
        for r in cur:
            out.append(r)

        # Test that the simple querying with no relational tables works
        self.assertEqual(out[0][0],'Gloomhaven')

        statement = '''SELECT m.Name FROM Mechanic AS m
            JOIN M2G AS jxn ON m.ID = jxn.MechanicId
            JOIN Game AS g ON g.ID = jxn.GameId'''
        cur.execute(statement)
        out2 = []
        for r in cur:
            out2.append(r)

        # Test that the many-to-many works
        self.assertEqual(out2[-2][0],'Storytelling')

class TestApp(unittest.TestCase):

    def testGetPlotDataTitle(self):
        out = am.get_plot_data('title')
        self.assertEqual(out[3,1],'Terraforming Mars')

    def testGetPlotDataDesigner(self):
        out = am.get_plot_data('designer')
        self.assertEqual(out[4,1],'Jacob Fryxelius')

    def testGetPlotDataPublisher(self):
        out = am.get_plot_data('publisher')
        self.assertEqual(out[21,1],'Riot Games')

    def testGetDetailDataTitle(self):
        outgame,outmech = am.get_detail_data('title','7 Wonders')
        self.assertEqual(outgame[0][2],'Repos Production')
        self.assertEqual(outmech[0][0],'Card Drafting')

    def testGetDetailDataDesigner(self):
        outgame,outmech = am.get_detail_data('designer','Jamey Stegmaier')
        self.assertEqual(outgame[0][1],4)

    def testGetDetailDataPublisher(self):
        outgame,outmech = am.get_detail_data('publisher','Fantasy Flight Games')
        self.assertEqual(outgame[0][1],25)

cac = 'unittest_cache.json'
info = 'unittest_info.json'
gi = db.crawl_top_games(num=1,cache_file=cac,info_dict_file=info)

unittest.main(verbosity=2,exit=False)

os.remove(cac)
os.remove(info)
os.remove('unittest.db')
