import os
import unittest

from CrawerImpl import Crawler91


class TestCrawlerMethods(unittest.TestCase):

    def test_get_fake_headers(self):
        headers = Crawler91().fake_headers()
        assert headers, 'get fake headers failed'

    def test_get_page_list(self):
        page_num = Crawler91().get_page_list()
        assert page_num, 'get page number failed'

    def test_download(self):
        Crawler91().download('https://dldir1.qq.com/qqfile/qq/QQ9.0.8/24201/QQ9.0.8.24201.exe', 'qq.exe')
        assert os.path.exists('qq.exe'), 'download failed'
