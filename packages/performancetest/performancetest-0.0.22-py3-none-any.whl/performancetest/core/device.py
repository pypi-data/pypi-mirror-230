# coding=utf-8
import os
import subprocess
import threading
import time
import traceback
from builtins import *
from io import BytesIO

import tidevice
from PIL import Image
from func_timeout import func_set_timeout
from tidevice import DataType
from tidevice._perf import RunningProcess, iter_cpu_memory, iter_gpu, iter_fps

from performancetest.core.command import ADB
from performancetest.core.global_data import logger


class AndroidDevice(object):
    def __init__(self, serialno, server_addr, package, save_dir):
        self.adb = ADB(serialno=serialno, server_addr=server_addr)
        self.serialno = serialno
        self.server_addr = server_addr
        self.package_pid = ''
        self.package = package
        self.save_dir = save_dir
        self.collect_logcat = threading.Thread(target=self._collect_logcat)
        self.sdkversion = self.get_sdkversion()

    def get_sdkversion(self):
        sdkversion = self.adb.raw_shell("getprop ro.build.version.sdk")
        logger.info("获取到的sdk版本号是{}".format(sdkversion))
        sdkversion = sdkversion.decode().strip()
        if sdkversion:
            return int(sdkversion)
        else:
            # 没有获取到sdkverison默认返回25
            return 25

    def get_front_app(self):
        lines: str = self.adb.raw_shell("dumpsys activity top | grep ACTIVITY").decode()
        logger.info("获取到的activty是{0}".format(lines))
        return lines.strip()

    def app_is_front(self):
        lines = self.get_front_app()
        lines = lines.split(os.linesep)
        for line in lines:
            if self.package in line:
                break
        else:
            raise Exception("app未启动")
        return (self.package in lines[-1]) and ("WebLandActivity" not in lines[-1]) and (
                "ali" not in lines[-1].lower()) and ("wx" not in lines[-1].lower())

    def get_packgelist(self):
        stdout = self.adb.raw_shell("pm list package")
        return stdout

    def is_install_package(self, package):
        stdout = self.adb.raw_shell("pm list package")
        logger.info("pm list package 返回内容：{0}".format(str(stdout)))
        if stdout.decode().find("package:" + package + os.linesep) > -1:
            return True
        else:
            return False

    def start_collect_logcat(self):
        self.collect_logcat.start()

    def _collect_logcat(self):
        with open(os.path.join(self.save_dir, "logcat.txt"), "w+") as f:
            pid = self.get_pid()
            collect_cmd = "adb logcat --pid=={}".format(pid)
            subprocess.run(collect_cmd.split(" "), stdout=f, stderr=f)

    def install_apk(self, apk_route):
        self.adb.raw_shell(["adb", "install", apk_route])

    @func_set_timeout(5)
    def stop_app(self):
        self.adb.raw_shell(["am", "force-stop", self.package])

    def start_app(self):  # 启动app
        self.adb.raw_shell(['monkey', '-p', self.package, '-c', 'android.intent.category.LAUNCHER', '1'])

    def get_pid(self):
        try:
            pid_infos = self.adb.raw_shell("ps | grep " + self.package).decode()
            real_pid = None
            pid_infos = pid_infos.splitlines()
            for pid in pid_infos:
                if pid.split()[-1] == self.package:
                    real_pid = pid.split()[1]
            if not real_pid:
                real_pid = pid_infos.split()[1]
            logger.info("测试包获取到的pid是{}".format(real_pid))
            self.package_pid = real_pid
            return real_pid
        except IndexError as e:
            logger.error("获取到的pid信息是{}".format(pid_infos))
            logger.exception(e)


class IosDevice(object):
    def __init__(self, serialno, device_addr, package, save_dir):
        self.serialno = serialno
        self.device = tidevice.Device(udid=self.serialno)
        self.device_addr = device_addr
        self.package = package
        self.save_dir = save_dir
        self.perf_dict_iter = dict()
        self.message_queue = []

    def start_app(self):  # 启动app
        self.device.app_start(self.package)

    def stop_app(self):
        self.device.app_stop(self.package)

    def get_battery(self):
        res = self.device.get_io_power()
        res_text = {"CurrentCapacity": (res['Diagnostics']['IORegistry']['CurrentCapacity']), "Temperature": (
            res['Diagnostics']['IORegistry']['Temperature'])}
        return res_text

    def get_perf(self):
        def callback(_type: DataType, value: dict):
            self.message_queue.append({"type": _type, "value": value})

        # with self.lock:
        current_item_key = self.serialno + "_" + self.package
        if not self.perf_dict_iter.get(current_item_key) or self.perf_dict_iter.get(current_item_key).get(
                "c_m_n")._stop_event.is_set():
            c_m_n = tidevice.Performance(self.device, [DataType.CPU, DataType.MEMORY])
            g_f = tidevice.Performance(self.device, [DataType.GPU, DataType.FPS])
            self.perf_dict_iter[current_item_key] = {"c_m_n": c_m_n, "g_f": g_f}
            self.message_queue = []
            try:
                c_m_n.start(self.package, callback=callback)
                g_f.start(self.package, callback=callback)
            except:
                traceback.print_exc()
                c_m_n.stop()
                g_f.stop()
                del self.perf_dict_iter[current_item_key]
        res_message = sorted(self.message_queue, key=lambda k: k["value"]["timestamp"])
        self.message_queue = []
        return res_message

    def stop_perf(self):
        current_item_key = self.serialno + "_" + self.package
        if self.perf_dict_iter.get(current_item_key):
            try:
                self.perf_dict_iter.get(current_item_key).get("c_m_n").stop()
            except:
                traceback.print_exc()
            try:
                self.perf_dict_iter.get(current_item_key).get("g_f").stop()
            except:
                traceback.print_exc()

    def gen_perf_info(self, key) -> list:
        cur_list: list = []
        cur_time = int(time.time() * 1000)
        dict_perf = self.perf_dict_iter[key]
        c_m = dict_perf.get("cm")
        fps = dict_perf.get("fps")
        gpu = dict_perf.get("gpu")
        c_type, c_value = next(c_m)
        c_value["timestamp"] = cur_time
        cur_list.append({"value": c_value, "type": c_type.lower()})
        c_type, c_value = next(c_m)
        c_value["timestamp"] = cur_time
        cur_list.append({"value": c_value, "type": c_type.lower()})
        c_type, c_value = next(fps)
        c_value["timestamp"] = cur_time
        cur_list.append({"value": c_value, "type": c_type.lower()})
        c_type, c_value = next(gpu)
        c_value["timestamp"] = cur_time
        cur_list.append({"value": c_value, "type": c_type.lower()})
        return cur_list

    def screenshot(self, filename):
        screenshot_image = self.device.screenshot()
        byte_stream = BytesIO()
        screenshot_image.save(byte_stream, format='PNG', quality_api=30)
        if byte_stream:
            image = Image.open(byte_stream)
            image.save(filename)
