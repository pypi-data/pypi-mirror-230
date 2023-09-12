# coding=utf-8

import csv
import re
import threading
import time
from builtins import *

from performancetest.core.base.monitor import Monitor
from performancetest.core.global_data import GlobalData as G, logger


class ParseNetworkInfo(object):
    def __init__(self, package, networkinfo, sdkversion=None):
        self.networkinfo = networkinfo
        self.package = package
        self.sdkversion = sdkversion
        self.network_data = self.get_network_data()

    def get_network_data(self):

        # define the regexp
        regexp = "wifi|wlan|rmnet"

        # process the network_info
        network_info = self.networkinfo.splitlines()[2:]
        acc_downFlow = 0
        acc_upFlow = 0
        for line in network_info:
            line_info = line.strip().split()
            if re.search(regexp, line_info[0]):
                acc_downFlow += float(line_info[1]) / 1024  # bytes  -> kb
                acc_upFlow += float(line_info[9]) / 1024
        network_info = [acc_downFlow, acc_upFlow]
        return network_info


class NetworkMonitor(Monitor):
    def __init__(self, save_file, test_time=-1, interval=1):
        super().__init__()
        self.save_file = save_file
        self.test_time = test_time
        self.interval = interval

    def get_network_info(self):

        # get packagename pid
        pid = G.device.get_pid()
        if pid is None:
            return None
        # get network info by pid
        network_info = G.device.adb.raw_shell(f"cat cat proc/{pid}/net/dev").decode()
        network_info = network_info.strip()
        network_info = ParseNetworkInfo(G.device.package, network_info, G.device.sdkversion).network_data
        logger.info("获取到的network信息是：{}".format(network_info))
        return network_info

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
        按照指定频率，循环搜集network的信息
        :return:
        '''
        network_title = ["timestamp", "realtime_downFlow", "realtime_upFlow", "sum_realtimeFlow",
                         "accumulate_downFlow", "accumulate_upFlow", "sum_accumFlow", ]
        network_file = self.save_file
        with open(network_file, 'w+') as df:
            csv.writer(df, lineterminator='\n').writerow(network_title)
        G.stop_event.set()  # 启动
        G.suspend_event.set()  # 启动
        last_timestamp = None
        last_acc_downFlow = None
        last_acc_upFlow = None
        accumulate_downFlow = 0
        accumulate_upFlow = 0
        while G.stop_event.is_set():
            G.suspend_event.wait()
            network_list = []
            try:
                logger.debug(
                    "---------------开始获取network信息, into _collect_package_network_thread loop thread is : " + str(
                        threading.current_thread().name))
                before = time.time()

                network_list.append(before)
                network_info = self.get_network_info()
                if last_timestamp and last_acc_downFlow:
                    realtime_downFlow = (diff_downFlow := (network_info[0] - last_acc_downFlow)) / (
                            before - last_timestamp)
                    realtime_upFlow = (diff_upFlow := (network_info[1] - last_acc_upFlow)) / (before - last_timestamp)
                    if diff_upFlow < 0 or diff_downFlow < 0 or network_info is None:
                        logger.info('程序切换进程id, 该秒流量不记入统计....')
                        last_timestamp = None
                        time.sleep(self.interval)
                        continue
                    else:
                        accumulate_downFlow += diff_downFlow
                        accumulate_upFlow += diff_upFlow
                else:
                    last_timestamp = before
                    last_acc_downFlow = network_info[0]
                    last_acc_upFlow = network_info[1]
                    time.sleep(self.interval)
                    continue
                network_list.extend([realtime_downFlow, realtime_upFlow, realtime_downFlow + realtime_upFlow])
                network_list.extend([accumulate_downFlow, accumulate_upFlow, accumulate_downFlow + accumulate_upFlow])
                last_timestamp = before
                last_acc_downFlow = network_info[0]
                last_acc_upFlow = network_info[1]
                after = time.time()
                time_consume = after - before
                logger.debug("  ============== time consume for network info : " + str(time_consume))
                if network_info == None or network_info == '':
                    logger.error("can't get network info, continue")

                    G.device.get_pid()

                    if G.run_mode != "airtest_monkey":
                        logger.info("重新获取pid,重启logcat")
                        G.logcat.restart()
                    continue

                with open(network_file, 'a+', encoding="utf-8") as df:
                    csv.writer(df, lineterminator='\n').writerow(network_list)
                    del network_list[:]
                delta_inter = self.interval - time_consume
                if delta_inter > 0:
                    time.sleep(delta_inter)
            except Exception as e:
                logger.error("an exception hanpend in network thread , reason unkown!, e:")
                logger.error(e)
                G.device.get_pid()
        logger.debug("network stop event is set or timeout")