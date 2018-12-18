import queue
import threading
import json

from CrawerImpl import Crawler91
from lib.print_with_time import time_print

# 定义下载的线程数
THREADS = 8


class MultiDownFromDatabase(threading.Thread):

    def __init__(self, q: queue.Queue, lock: threading.Lock):
        super().__init__()
        self.daemon = True
        self._q = q
        self._lock = lock

    def run(self):
        craw = Crawler91()
        while True:
            name, url = self._q.get()
            try:
                time_print('-[{0}]-开始解析： {1}'.format(self.getName(), name + '.mp4'))
                real_url_or_html = craw.parse_video_real_link(url)
                time_print('-[{0}]-解析真实视频地址完毕，地址: {1}'.format(self.getName(), real_url_or_html))
                time_print('-[{0}]-开始下载文件: {1}'.format(self.getName(), name + '.mp4'))
                craw.aria2_download(real_url_or_html, name + '.mp4')
                time_print('-[{0}]-下载文件结束，更新记录文件'.format(self.getName(), name + '.mp4'))
                self._lock.acquire()
                update_crawler_data_file(name)
                self._lock.release()
                self._q.task_done()
                time_print('-[{0}]-更新记录文件完毕，等待下一个任务'.format(self.getName()))
            except ValueError as e:
                time_print('-[{0}]-解析真实视频地址失败,{1}'.format(self.getName(), e))


def update_crawler_data_file(name: str) -> None:
    with open('Current91.txt') as f:
        from_file_data = json.loads(f.read())

    for i in from_file_data:
        if name in i:
            i['isDownload'] = 1

    with open('Current91.txt', 'w') as f:
        f.write(json.dumps(from_file_data))


def multi_thread_down():
    craw = Crawler91()
    page_list = craw.get_page_list()
    crawled_data = []
    video_name_and_url_dict = {}  # 由于发现有时候抓取的视频名称一样，这样就可以去重
    time_print('开始解析视频名称和地址')
    for i in range(1, page_list + 1):
        video_name_and_url_dict.update(craw.get_video_name_and_url(craw.main_page_url + '&page=' + str(i)))
    for i in video_name_and_url_dict:
        file_dict = {i: video_name_and_url_dict[i], 'isDownload': 0}
        crawled_data.append(file_dict)
    # 将得到的结果写入文件
    with open('Current91.txt', 'w') as f:
        f.write(json.dumps(crawled_data))

    q = queue.Queue()
    my_lock = threading.Lock()

    time_print('准备多线程解析，下载')
    for i in range(THREADS):
        t = MultiDownFromDatabase(q, my_lock)
        t.start()

    for i in video_name_and_url_dict:
        q.put((i, video_name_and_url_dict[i]))
    q.join()


if __name__ == '__main__':
    multi_thread_down()
