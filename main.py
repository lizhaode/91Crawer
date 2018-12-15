import queue
import threading

from CrawerImpl import Crawler91
from lib.print_with_time import time_print

# 定义下载的线程数
THREADS = 5


class MultiDownFromDatabase(threading.Thread):

    def __init__(self, q: queue.Queue):
        super().__init__()
        self.daemon = True
        self._q = q

    def run(self):
        craw = Crawler91()
        while True:
            name, url = self._q.get()
            try:
                time_print('开始解析： {0}'.format(name))
                real_url_or_html = craw.parse_video_real_link(url)
                craw.aria2_download(real_url_or_html, name + '.mp4')
                self._q.task_done()
            except ValueError as e:
                time_print('\n解析真实视频地址失败,{0}'.format(e))


def multi_thread_down():
    craw = Crawler91()
    page_list = craw.get_page_list()
    video_name_and_url_dict = {}  # 由于发现有时候抓取的视频名称一样，这样就可以去重
    time_print('开始解析视频名称和地址')
    for i in range(1, page_list + 1):
        video_name_and_url_dict.update(craw.get_video_name_and_url(craw.main_page_url + '&page=' + str(i)))

    q = queue.Queue()

    time_print('准备多线程解析，下载')
    for i in range(THREADS):
        t = MultiDownFromDatabase(q)
        t.start()

    for i in video_name_and_url_dict:
        q.put((i, video_name_and_url_dict[i]))
    q.join()


if __name__ == '__main__':
    multi_thread_down()
