import os
import unittest

from main import Crawler91


class TestCrawlerMethods(unittest.TestCase):

    def test_normal_create_database(self):
        if os.path.isfile('current91.db'):
            os.remove('current91.db')
        Crawler91().create_database()
        assert os.path.isfile('current91.db'), 'create database failed'

    def test_abnormal_create_database(self):
        if not os.path.isfile('current91.db'):
            with open('current91.db', 'w') as f:
                f.write('test')
        Crawler91().create_database()
        assert os.path.isfile('current91.db'), 'create database failed'
