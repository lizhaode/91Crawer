import sqlite3
import os
from lib.print_with_time import time_print


class ControlSqliteDatabase:

    def __init__(self, is_create_database: bool):
        if is_create_database:
            conn, cursor = self.create_database()
            self._conn = conn
            self._cursor = cursor
        else:
            self._conn = sqlite3.connect('current91.db')
            self._cursor = self._conn.cursor()

    def close_database(self):
        self._cursor.close()
        self._conn.close()

    @staticmethod
    def create_database() -> tuple:
        if os.path.isfile('current91.db'):
            os.remove('current91.db')

        conn = sqlite3.connect('current91.db')
        cursor = conn.cursor()

        create_database_sentence = '''CREATE TABLE craw_url
            (id INTEGER PRIMARY KEY AUTOINCREMENT,
            name text UNIQUE,
            url text UNIQUE,
            is_download INT DEFAULT 0)'''

        cursor.execute(create_database_sentence)
        conn.commit()

        return conn, cursor

    def get_url_from_database(self) -> list:
        """
        返回结果是个list，类似于 [(id,name,url),(id,name,url)] 形式
        """

        select_sql = 'SELECT `id`,name,url FROM craw_url WHERE is_download = 0'
        self._cursor.execute(select_sql)
        all_result = self._cursor.fetchall()

        return all_result

    def write_info_to_database(self, info_dict: dict) -> None:
        for i in info_dict.keys():
            insert_sentence = 'INSERT INTO craw_url (name,url) VALUES (:name,:url)'
            self._cursor.execute(insert_sentence, {'name': i, 'url': info_dict[i]})
            self._conn.commit()

    def update_isdownload(self, craw_id: int, file_name: str) -> None:
        update_sentence = "UPDATE craw_url set is_download = 1 where `id` = {0} AND is_download = 0".format(craw_id)
        time_print('{0}下载完毕，开始更新状态'.format(file_name))
        self._cursor.execute(update_sentence)
        self._conn.commit()
        time_print('{0}状态更新完毕'.format(file_name))
