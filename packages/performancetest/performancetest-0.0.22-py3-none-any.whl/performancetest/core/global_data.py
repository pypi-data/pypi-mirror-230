# coding=utf-8
import logging
import os
import threading
from builtins import *
from logging.handlers import RotatingFileHandler

logger = logging.getLogger(__file__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(module)s - %(message)s')
handler = RotatingFileHandler('log.log', maxBytes=100 * 1024 * 1024, backupCount=5)
handler.setFormatter(formatter)
logger.addHandler(handler)


class GlobalData(object):
    suspend_event = threading.Event()  # 暂停,默认值是False，False是暂停，True是运行中
    stop_event = threading.Event()  # 停止，默认是False，False 是停止， True 是运行中
