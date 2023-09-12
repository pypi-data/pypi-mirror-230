# coding=utf-8
import threading
import time
from builtins import *
from pathlib import Path
from airtest.core.android import Android
from func_timeout import func_set_timeout, FunctionTimedOut

from performancetest.core.base.monitor import Monitor
from performancetest.core.global_data import GlobalData as G, logger


class SnapshotMonitor(Monitor):
    def __init__(self, save_dir, serialno, server_addr, interval=1, test_time=-1):
        super().__init__()
        self.save_dir = self.get_save_file(save_dir)
        self.interval = interval
        self.device = Android(serialno, host=server_addr)

    def get_save_file(self, save_dir):
        save_dir = Path(save_dir)
        if not save_dir.is_dir():
            save_dir.mkdir(parents=True, exist_ok=True)
        return save_dir

    def snapshot(self, name):
        self.device.snapshot(filename=name)

    def start(self):
        super(Monitor, self).start()

    # 结束任务
    def stop(self):
        G.stop_event.clear()

    # 暂停任务
    def suspend(self):
        G.suspend_event.clear()

    def run(self):
        '''
        按照指定频率手机截图
        '''
        logger.info("开始保存图片")
        G.stop_event.set()  # 启动
        G.suspend_event.set()  # 启动
        while G.stop_event.is_set():  # 停止了循环会停止
            G.suspend_event.wait()  # 暂停时会暂停在这里
            try:
                logger.debug(
                    "---------------开始截图, _collect_screenshot loop thread is : " + str(
                        threading.current_thread().name))
                before = time.time()
                self.snapshot(self.save_dir.joinpath(str(int(before * 1000)) + ".jpg"))
                after = time.time()
                time_consume = after - before
                logger.debug("  ============== time consume snapshot time : " + str(time_consume))
                delta_inter = self.interval - time_consume
                if delta_inter > 0:
                    time.sleep(delta_inter)
            except Exception as e:
                logger.error("an exception hanpend in snapshot thread , reason unkown!, e:")
                logger.exception(e)
        logger.debug("snapshot stop")


class IosSibSnapshotMonitor(Monitor):
    def __init__(self, save_dir, device, package, interval=1, test_time=-1):
        super(IosSibSnapshotMonitor, self).__init__()
        self.save_dir = self.get_save_file(save_dir)
        self.interval = interval
        self.package = package
        self.device = device
        self.screenshot_collect = threading.Thread(target=self._collect_screenshot, args=(test_time,))
        self.running = False
        self.G = G

    def get_save_file(self, save_dir):
        save_dir = Path(save_dir)
        if not save_dir.is_dir():
            save_dir.mkdir(parents=True, exist_ok=True)
        return save_dir

    @func_set_timeout(10)
    def snapshot(self, name):
        self.device.screenshot(name)

    def start(self):
        self.screenshot_collect.start()

    def stop(self):
        logger.info("close")

    def _collect_screenshot(self, test_time):
        '''
        按照指定频率手机截图
        '''
        logger.info("开始保存图片")
        G = self.G
        G.stop_event.set()
        while G.stop_event.is_set():
            try:
                logger.debug(
                    "---------------开始截图, _collect_screenshot loop thread is : " + str(
                        threading.current_thread().name))
                before = time.time()
                self.snapshot(self.save_dir.joinpath(str(int(before * 1000)) + ".jpg"))
                after = time.time()
                time_consume = after - before
                logger.debug("  ============== time consume snapshot time : " + str(time_consume))
                delta_inter = self.interval - time_consume
                if delta_inter > 0:
                    time.sleep(delta_inter)
            except (Exception, FunctionTimedOut) as e:
                logger.error("an exception hanpend in snapshot thread , reason unkown!, e:")
                logger.exception(e)
                time.sleep(0.5)
        logger.debug("snapshot stop")
