# coding=utf-8
import csv
import logging
import os
import threading
import time
import traceback
from builtins import *

from performancetest.core.base.monitor import Monitor
from performancetest.core.global_data import logger


class IosPerfMonitor(Monitor):
    def __init__(self, save_dir, G, test_time=-1, interval=1):
        super().__init__()
        self.save_dir = save_dir
        self.G = G
        self.test_time = test_time
        self.interval = interval
        self.property_all = {
            "cpu": (os.path.join(self.save_dir, "cpu.csv"), ["timestamp", "cpu%"]),
            "memory": (os.path.join(self.save_dir, "memory.csv"), ["timestamp", "memory"]),
            "fps": (os.path.join(self.save_dir, "fps.csv"),
                    ["timestamp", "FPS", "lag_number", "FPS_full_number", "jank_number", "big_jank_number"]),
            "gpu": (os.path.join(self.save_dir, "gpu.csv"), ["timestamp", "gpu%"]),
            "devicebattery": (os.path.join(self.save_dir, "devicebattery.csv"),
                              ["timestamp", "devicetemperature", "devicebatterylevel", "charge"]),
            "network": (os.path.join(self.save_dir, "network.csv"), ["timestamp", "realtime_downFlow", "realtime_upFlow", "sum_realtimeFlow",
                         "accumulate_downFlow", "accumulate_upFlow", "sum_accumFlow", ]),
        }
        for k, v in self.property_all.items():
            with open(v[0], 'w+') as df:
                logger.info('-------------------初始csv')
                csv.writer(df, lineterminator='\n').writerow(v[1])
        self.ios_perf_collect = [
            threading.Thread(target=self._collect_package_ios_perf_all_thread),
            threading.Thread(target=self._collect_ios_battery_thread)
        ]

    def get_perf_info(self):
        """
            target_o:  cpu, mem, gpu, fps
        """
        G = self.G
        res_line = G.device.get_perf()
        return res_line

    def get_battery(self):
        G = self.G
        battery_info = G.device.get_battery()
        battery_info_res = dict()
        battery_info_res['battery'] = battery_info['CurrentCapacity']
        battery_info_res['level'] = battery_info['Temperature'] / 100
        return battery_info_res

    def start(self):
        # to do 后续监控进程是否存在  来重启线程
        for th in self.ios_perf_collect:
            th.start()

    # 结束任务
    def stop(self):
        G = self.G
        G.device.stop_perf()
        self.G.stop_event.clear()


    # 暂停任务
    def suspend(self):
        self.G.suspend_event.clear()

    def _collect_package_ios_perf_all_thread(self):
        G = self.G
        G.stop_event.set()
        G.suspend_event.set()
        for k, v in self.property_all.items():
            if k == "devicebattery":
                continue
            with open(v[0], 'w+') as df:
                csv.writer(df, lineterminator='\n').writerow(v[1])
        while G.stop_event.is_set():
            try:
                logging.debug("---------------开始获取所有性能信息" + str(
                    threading.current_thread().name))
                before = time.time()
                perf_line_list = self.get_perf_info()  # 可超时的任务
                if not perf_line_list:
                    time.sleep(1)
                    continue
                for perf_line in perf_line_list:
                    logging.info("---iosperf 获取到数据 {0}".format('performance: ', perf_line))
                    file_path = self.property_all.get(perf_line.get("type"))
                    if not file_path:
                        time.sleep(0.2)
                        continue
                    values = perf_line.get("value")
                    value_list = [values.get("timestamp") // 1000, str(values.get("value"))]
                    with open(file_path[0], 'a+', encoding="utf-8") as df:
                        logging.info("write {0}".format(value_list))
                        csv.writer(df, lineterminator='\n').writerow(value_list)
                        del value_list[:]
                after = time.time()
                time_consume = after - before
                delta_inter = self.interval - time_consume
                if delta_inter > 0:
                    time.sleep(delta_inter)
            except Exception as e:
                logging.error("an exception hanpend in ios perf thread , reason unkown!, e: iosperf")
                logging.error(e)
                logging.error(traceback.format_exc())
                after = time.time()
                time_consume = after - before
                delta_inter = self.interval - time_consume
                if delta_inter > 0:
                    time.sleep(delta_inter)
        logging.debug("stop event is set or timeout iosperf")

    def _collect_ios_battery_thread(self):
        G = self.G
        G.stop_event.set()
        G.suspend_event.set()
        with open(self.property_all.get("devicebattery")[0], 'w+') as df:
            csv.writer(df, lineterminator='\n').writerow(self.property_all.get("devicebattery")[1])
        while G.stop_event.is_set():
            try:
                logging.debug("---------------开始获取battery性能信息" + str(
                    threading.current_thread().name))
                before = time.time()
                battery_dict = self.get_battery()  # 可超时的任务
                if not battery_dict:
                    time.sleep(0.2)
                    continue
                write_info = []
                write_info.append(int(time.time()))
                write_info.append(battery_dict.get("level"))
                write_info.append(battery_dict.get("battery"))
                write_info.append("true")
                with open(self.property_all.get("devicebattery")[0], 'a+', encoding="utf-8") as df:
                    logging.info("write devicebattery {0}".format(write_info))
                    csv.writer(df, lineterminator='\n').writerow(write_info)
                    del write_info[:]
                after = time.time()
                time_consume = after - before
                delta_inter = self.interval - time_consume
                if delta_inter > 0:
                    time.sleep(delta_inter)
            except Exception as e:
                logging.error("an exception hanpend in ios perf thread , reason unkown!, e: iosperf")
                logging.error(e)
                logging.error(traceback.format_exc())
        logging.debug("stop event is set or timeout iosperf")
