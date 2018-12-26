import queue
import threading
import json
from lib.CrawerImpl import Crawler91
from lib.print_with_time import time_print


def update_crawler_data_file(name: str) -> None:
    with open('Current91.json') as f:
        from_file_data = json.loads(f.read())

    for i in from_file_data:
        if name in i:
            i['isDownload'] = 1

    with open('Current91.json', 'w') as f:
        f.write(json.dumps(from_file_data))


class MultiDownloadFromQueue(threading.Thread):

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
