import os
import random
import re
import subprocess

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from lib.print_with_time import time_print


class Crawler91:

    def __init__(self):

        self.main_page_url = 'http://91porn.com/v.php?category=long&viewtype=basic'

    def fake_headers(self) -> dict:

        random_ip = str(random.randint(0, 255)) + '.' + str(random.randint(0, 255)) + '.' + str(
            random.randint(0, 255)) + '.' + str(random.randint(0, 255))

        headres = {
            'Accept-Language': 'zh-CN,zh;q=0.9',
            "User-Agent": UserAgent().random,
            'X-Forwarded-For': random_ip
        }
        return headres

    def get_page_list(self):

        response = requests.get(self.main_page_url)
        bs = BeautifulSoup(response.text, "lxml")
        pages = bs.find_all(href=re.compile('category=long&viewtype=basic&page='))[-2].text
        time_print('解析所有视频页数完毕，返回结果')
        return int(pages)

    def get_video_name_and_url(self, page_url: str) -> dict:

        response = requests.get(page_url, headers=self.fake_headers())
        bs = BeautifulSoup(response.text, 'lxml')

        all_video_dict = {}

        for i in bs.find_all('div', 'listchannel'):
            video_name = i.find('a', title=True)['title']
            video_url = i.find('a', title=True)['href']
            # 去掉名称中的空格
            video_name = video_name.replace(' ', '')
            all_video_dict.update({video_name: video_url})

        return all_video_dict

    def parse_video_real_link(self, page_url: str) -> str:

        response = requests.get(page_url, headers=self.fake_headers())
        try:
            bs = BeautifulSoup(response.text, 'lxml')
            real_link = bs.find('video').find('source')['src']

            # 原始网页中抓取的链接中除了 http:// 外还包含 // ，应该替换成 /
            tmp_link_list = real_link.split('//')
            real_link = tmp_link_list[0] + '//' + tmp_link_list[1] + '/' + tmp_link_list[2]

            time_print('解析真实视频地址完毕，地址: {0}'.format(real_link))
            return real_link
        except AttributeError:
            raise ValueError('parse video down link false')

    def download(self, video_url: str, file_name: str) -> None:

        # 创建91Crawer目录
        if os.path.exists('91Crawer') is False:
            os.mkdir('91Crawer')

        with requests.get(video_url, headers=self.fake_headers(), stream=True) as r:
            write_file = open('91Crawer/' + file_name, 'wb')
            time_print('开始写入文件: {0}'.format(file_name))
            for i in r.iter_content(chunk_size=20971520):
                write_file.write(i)
            write_file.close()

    def aria2_download(self, video_url: str, file_name: str) -> None:

        crawer_path = 'videos'

        # 创建91Crawer目录
        if os.path.exists(crawer_path) is False:
            os.mkdir(crawer_path)

        time_print('开始多线程下载文件: {0}'.format(file_name))
        down_command = 'aria2c -x 16 "{0}" -d "{1}" -o "{2}"'.format(video_url, crawer_path,
                                                                     file_name)
        subprocess.check_output(down_command, shell=True)
