import os
import random
import re
import requests
import sqlite3
import subprocess
import time
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


class Crawer91:

    def __init__(self):

        self.main_page_url = 'http://91porn.com/v.php?category=long&viewtype=basic'

    def time_print(self,print_str):

        print('[' + time.strftime('%m/%d-%H:%M:%S') + ']' + print_str)

    def create_database(self):

        if os.path.isfile('current91.db'):
            os.remove('current91.db')

        conn = sqlite3.connect('current91.db')
        cursor = conn.cursor()

        create_database = '''CREATE TABLE craw_url
                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                name text UNIQUE,
                url text UNIQUE,
                is_download INT DEFAULT 0)'''

        cursor.execute(create_database)
        conn.commit()
        cursor.close()
        conn.close()

    def write_info_to_database(self, info_dict):

        conn = sqlite3.connect('current91.db')
        cursor = conn.cursor()

        for i in info_dict.keys():
            insert_sql = 'INSERT INTO craw_url (name,url) VALUES (:name,:url)'
            cursor.execute(insert_sql, {'name': i, 'url': info_dict[i]})
            conn.commit()
        cursor.close()
        conn.close()

    def get_url_from_database(self):

        '''
        返回结果是个list，类似于 [(name,url),(name,url)] 形式
        '''

        conn = sqlite3.connect('current91.db')
        cursor = conn.cursor()

        select_sql = 'SELECT `id`,name,url FROM craw_url WHERE is_download = 0'
        cursor.execute(select_sql)
        all_result = cursor.fetchall()
        cursor.close()
        conn.close()

        return all_result

    def update_isdownload(self, craw_id):

        conn = sqlite3.connect('current91.db')
        cursor = conn.cursor()

        update_sql = "UPDATE craw_url set is_download = 1 where `id` = {0} AND is_download = 0".format(craw_id)
        self.time_print('下载完毕，开始更新状态')
        cursor.execute(update_sql)
        conn.commit()
        cursor.close()
        conn.close()
        self.time_print('状态更新完毕')

    def fake_headers(self):

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
        self.time_print('解析所有视频页数完毕，返回结果')
        return int(pages)

    def get_video_name_and_url(self, page_url):

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

    def parse_video_real_link(self, page_url):

        response = requests.get(page_url, headers=self.fake_headers())
        try:
            bs = BeautifulSoup(response.text, 'lxml')
            real_link = bs.find('video').find('source')['src']
            self.time_print('解析真实视频地址完毕，地址: {0}'.format(real_link))
            return real_link
        except AttributeError:
            return response.text

    def download(self, video_url, file_name):

        # 创建91Crawer目录
        if os.path.exists('91Crawer') is False:
            os.mkdir('91Crawer')

        with requests.get(video_url, headers=self.fake_headers(), stream=True) as r:
            write_file = open('91Crawer/' + file_name, 'wb')
            self.time_print('开始写入文件: {0}'.format(file_name))
            for i in r.iter_content(chunk_size=20971520):
                write_file.write(i)
            write_file.close()

    def aria2_download(self,video_url,file_name):

        # 创建91Crawer目录
        if os.path.exists('91Crawer') is False:
            os.mkdir('91Crawer')

        down_command = 'aria2c -x 16 "{0}" -o "{1}"'.format(video_url,'91Crawer/' + file_name)
        subprocess.check_output(down_command,shell=True)


if __name__ == '__main__':
    crawer_91 = Crawer91()
    # 创建数据库，注意：会删除现有的库
    crawer_91.create_database()
    # 开始获取网页的信息
    page_list = crawer_91.get_page_list()
    video_name_and_url_dict = {}  # 由于发现有时候抓取的视频名称一样，这样就可以去重
    crawer_91.time_print('开始解析视频名称和地址')
    for i in range(1, page_list + 1):
        video_name_and_url_dict.update(crawer_91.get_video_name_and_url(crawer_91.main_page_url + '&page=' + str(i)))
    # 将获取到的视频名称和url写入数据库，如果此次只是下载之前下载失败的，这句之前都注释掉即可
    crawer_91.time_print('分析视频结束，去重后一共获取到{0}个视频'.format(len(video_name_and_url_dict.keys())))
    crawer_91.write_info_to_database(video_name_and_url_dict)
    crawer_91.time_print('写入数据库结束，开始下载')

    while True:
        database_list = crawer_91.get_url_from_database()
        if database_list:
            for j in database_list:
                try:
                    crawer_91.time_print('开始解析： {0}'.format(j[1]))
                    real_url_or_html = crawer_91.parse_video_real_link(j[2])
                    crawer_91.aria2_download(real_url_or_html, j[1] + '.mp4')
                except Exception:
                    crawer_91.time_print('\n解析真实视频地址失败，贴出网页html：')
                    crawer_91.time_print(real_url_or_html)
                    continue

                crawer_91.update_isdownload(j[0])
        else:
            break
