# coding=utf-8

import csv
import os
import threading
import time
import traceback
from builtins import *
import re
from performancetest.core.base.monitor import Monitor
from performancetest.core.global_data import GlobalData as G, logger


class ParseCpuInfo(object):
    def __init__(self, package, cpuinfo, sdkversion=None):
        self.cpuinfo = cpuinfo
        self.package = package
        self.sdkversion = sdkversion
        self.cpu_rate = self.get_cpu_rate()

    def get_cpu_rate(self):
        for pidinfo in self.cpuinfo.split(os.linesep):
            if self.package in pidinfo:
                pidinfo = pidinfo.split()
                if pidinfo[-1] == self.package:
                    return pidinfo[4].replace("%", '')
        return ''


class CpuMonitor(Monitor):
    def __init__(self, save_file, test_time=-1, interval=1):
        super().__init__()
        self.save_file = save_file
        self.test_time = test_time
        self.interval = interval

    def getprocessCpuStat(self):
        """get the cpu usage of a process at a certain time"""
        cmd = 'cat /proc/{}/stat'.format(G.device.get_pid())
        result = G.device.adb.raw_shell(cmd).decode()
        r = re.compile("\\s+")
        toks = r.split(result)
        processCpu = float(toks[13]) + float(toks[14]) + float(toks[15]) + float(toks[16])
        return processCpu

    def getTotalCpuStat(self):
        """get the total cpu usage at a certain time"""
        cmd = 'cat /proc/stat | grep ^cpu'
        result = G.device.adb.raw_shell(cmd).decode()
        r = re.compile(r'(?<!cpu)\d+')
        toks = r.findall(result)

        totalCpu = 0
        for i in range(1, 9):
            totalCpu += float(toks[i])
        return float(totalCpu)

    def getCpuCores(self):
        """get Android cpu cores"""
        cmd = 'cat /sys/devices/system/cpu/online'
        result = G.device.adb.raw_shell(cmd).decode()
        try:
            nums = int(result.split('-')[1]) + 1
        except:
            nums = 1
        return nums

    def getSysCpuStat(self):
        """get the total cpu usage at a certain time"""
        cmd = 'cat /proc/stat | grep ^cpu'
        result = G.device.adb.raw_shell(cmd).decode()
        r = re.compile(r'(?<!cpu)\d+')
        toks = r.findall(result)
        ileCpu = float(toks[4])
        sysCpu = self.getTotalCpuStat() - ileCpu
        return sysCpu

    def getAndroidCpuRate(self):
        """get the Android cpu rate of a process"""
        try:
            processCpuTime_1 = self.getprocessCpuStat()
            totalCpuTime_1 = self.getTotalCpuStat()
            sysCpuTime_1 = self.getSysCpuStat()
            time.sleep(0.5)
            processCpuTime_2 = self.getprocessCpuStat()
            totalCpuTime_2 = self.getTotalCpuStat()
            sysCpuTime_2 = self.getSysCpuStat()
            appCpuRate = round(float((processCpuTime_2 - processCpuTime_1) / (totalCpuTime_2 - totalCpuTime_1) * 100),
                               2)
            sysCpuRate = round(float((sysCpuTime_2 - sysCpuTime_1) / (totalCpuTime_2 - totalCpuTime_1) * 100), 2)
        except:
            appCpuRate, sysCpuRate = 0, 0
            traceback.print_exc()
        return appCpuRate, sysCpuRate

    def get_cpuinfo(self):
        if G.device.sdkversion >= 25:
            cpu_info = G.device.adb.raw_shell("top -n 1 -p {} -o %CPU -b -q".format(G.device.package_pid)).decode()
            cpu_info = cpu_info.strip()
        else:
            cpu_info = G.device.adb.raw_shell("top -n 1".format(G.device.package_pid)).decode()
            cpu_info = ParseCpuInfo(G.device.package, cpu_info, G.device.sdkversion).cpu_rate
        logger.info("获取到的cpu信息是：{}".format(cpu_info))
        return cpu_info

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
        按照指定频率，循环搜集cpu的信息
        :return:
        '''
        cpu_title = ["timestamp", "cpu%", "proc_cpu%", "proc_sys_cpu%"]
        cpu_file = self.save_file
        with open(cpu_file, 'w+') as df:
            csv.writer(df, lineterminator='\n').writerow(cpu_title)
        G.stop_event.set()  # 启动
        G.suspend_event.set()  # 启动
        while G.stop_event.is_set():  # 停止了循环会停止
            G.suspend_event.wait()  # 暂停时会暂停在这里
            cpu_list = []
            try:
                logger.debug("---------------开始获取cpu信息, into _collect_package_cpu_thread loop thread is : " + str(
                    threading.current_thread().name))
                before = time.time()
                cpu_list.append(before)
                # 为了cpu值的准确性，将采集的时间间隔放在top命令中了
                cpu_info = self.get_cpuinfo()
                proc_app_cpu, proc_sys_cpu = self.getAndroidCpuRate()
                cpu_list.append(cpu_info)
                cpu_list.append(proc_app_cpu)
                cpu_list.append(proc_sys_cpu)
                after = time.time()
                time_consume = after - before
                logger.debug(
                    "============== time consume for cpu info : {0}, value {1}".format(time_consume, cpu_info))
                if cpu_info == None or cpu_info == '' or float(cpu_info) == 0:
                    logger.error("top can't get cpu info")
                    G.device.get_pid()
                    logger.info("重新获取pid,重启logcat")
                    # 取消获取不到跳过，默认给0
                    cpu_list[-1] = 0
                with open(cpu_file, 'a+', encoding="utf-8") as df:
                    csv.writer(df, lineterminator='\n').writerow(cpu_list)
                    del cpu_list[:]
                delta_inter = self.interval - time_consume
                if delta_inter > 0:
                    time.sleep(delta_inter)
            except Exception as e:
                logger.error("an exception hanpend in cpu thread , reason unkown!, e:")
                traceback.print_exc()
                G.device.get_pid()
        logger.debug("cpu stop event is set or timeout")
