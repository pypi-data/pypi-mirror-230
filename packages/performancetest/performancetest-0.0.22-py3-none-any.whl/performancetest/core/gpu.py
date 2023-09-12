# coding=utf-8

import csv
import threading
import time
import traceback
from builtins import *

from performancetest.core.base.monitor import Monitor
from performancetest.core.global_data import GlobalData as G, logger


class GpuMonitor(Monitor):
    def __init__(self, save_file, test_time=-1, interval=1):
        super().__init__()
        self.save_file = save_file
        self.test_time = test_time
        self._stop_event = threading.Event()
        self.interval = interval

    def get_gpuinfo(self):
        gpu_info = G.device.adb.raw_shell("cat /sys/class/kgsl/kgsl-3d0/gpubusy").decode()
        gpu_info = gpu_info.strip()
        res_n = gpu_info.split(" ")
        for i in range(len(res_n) - 1, -1, -1):
            if res_n[i] == '':
                res_n.pop(i)
        gpu_info = 0
        try:
            gpu_info = int(res_n[0]) / int(res_n[1]) * 100
        except:
            pass
        logger.info("获取到的gpu信息是：{}".format(gpu_info))
        return gpu_info

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
        按照指定频率，循环搜集gpu的信息
        :return:
        '''
        gpu_title = ["timestamp", "gpu%"]
        gpu_file = self.save_file
        with open(gpu_file, 'w+') as df:
            csv.writer(df, lineterminator='\n').writerow(gpu_title)
        G.stop_event.set()  # 启动
        G.suspend_event.set()  # 启动
        while G.stop_event.is_set():  # 停止了循环会停止
            G.suspend_event.wait()  # 暂停时会暂停在这里
            gpu_list = []
            try:
                logger.debug("---------------开始获取gpu信息, into _collect_package_gpu_thread loop thread is : " + str(
                    threading.current_thread().name))
                before = time.time()
                gpu_list.append(before)
                # 为了gpu值的准确性，将采集的时间间隔放在top命令中了
                gpu_info = self.get_gpuinfo()
                gpu_list.append(gpu_info)
                after = time.time()
                time_consume = after - before
                logger.debug("  ============== time consume for gpu info : " + str(time_consume))
                if gpu_info == None or gpu_info == '' or float(gpu_info) == 0:
                    logger.error("can't get gpu info")
                    G.device.get_pid()
                    # 取消获取不到跳过，默认给0
                    gpu_list[-1] = 0
                with open(gpu_file, 'a+', encoding="utf-8") as df:
                    csv.writer(df, lineterminator='\n').writerow(gpu_list)
                    del gpu_list[:]
                delta_inter = self.interval - time_consume
                if delta_inter > 0:
                    time.sleep(delta_inter)
            except Exception as e:
                logger.error("an exception hanpend in gpu thread , reason unkown!, e:")
                logger.error(e)
                traceback.print_exc()
                G.device.get_pid()
        logger.debug("gpu stop event is set or timeout")
