import queue
import threading
import json

from lib.CrawerImpl import Crawler91
from lib.MultiThreadDownload import MultiDownloadFromQueue
from lib.print_with_time import time_print

# 定义下载的线程数
THREADS = 8


def get_and_multi_thread_down():
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
    with open('Current91.json', 'w') as f:
        f.write(json.dumps(crawled_data))

    q = queue.Queue()
    my_lock = threading.Lock()

    time_print('准备多线程解析，下载')
    for i in range(THREADS):
        t = MultiDownloadFromQueue(q, my_lock)
        t.start()

    for i in video_name_and_url_dict:
        q.put((i, video_name_and_url_dict[i]))
    q.join()


def only_multi_thread_down():
    with open('Current91.json') as f:
        ori_task_list = json.loads(f.read())

    q = queue.Queue()
    my_lock = threading.Lock()

    time_print('准备多线程解析，下载')
    for i in range(THREADS):
        t = MultiDownloadFromQueue(q, my_lock)
        t.start()

    for i in ori_task_list:
        if i.pop('isDownload') == 0:
            for j, k in i.items():
                q.put((j, k))
    q.join()


if __name__ == '__main__':
    get_and_multi_thread_down()
    # only_multi_thread_down()
