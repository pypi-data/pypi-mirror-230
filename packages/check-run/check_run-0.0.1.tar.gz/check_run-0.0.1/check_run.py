# -*-*-*-*-*- encoding: utf-8 -*-*-*-*-
# @File  :   check_run.py
# @Author :  stonepy
# @CreateTime：2023/8/10 18:08
# -*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-
import hashlib
import json
import logging
import os
import sys
import time


class RunningException(Exception):
    pass


class Check:
    def __init__(self, check_second_time=300):
        self.check_second_time = check_second_time
        self.cache_dir = os.path.join(os.path.expanduser('~'), '.check_ran')
        self.file_path = os.path.join(self.cache_dir, 'check_ran.json')
        os.makedirs(self.cache_dir, exist_ok=True)

    def check(self):
        data = {}
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r') as f:
                data = json.load(f)
        md5_str = self._md5(sys.argv[0])
        is_ran = self._check(md5_str, data)
        if is_ran:
            logging.warning("意外的重复运行,上次运行时间为: %s", data[md5_str]['start'])
            exit(1)
        write_data = {
            "start": int(time.time())
        }
        data[md5_str] = write_data
        self._save(data)

    def _save(self, data):
        with open(self.file_path, 'w') as f:
            json.dump(data, f)

    def _check(self, md5_str, data):
        if md5_str not in data:
            return False
        start_time = data[md5_str]['start']
        if time.time() - start_time > self.check_second_time:
            return False
        return True

    def set_cache_dir(self, cache_dir):
        self.cache_dir = cache_dir

    @staticmethod
    def _md5(input_str):
        md5 = hashlib.md5()
        md5.update(input_str.encode('utf-8'))
        return md5.hexdigest()
