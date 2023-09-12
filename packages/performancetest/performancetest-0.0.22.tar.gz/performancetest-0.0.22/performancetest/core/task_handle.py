# coding=utf-8
import os
import time
import traceback
from builtins import *
import datetime
from multiprocessing.context import Process
from performancetest.core.base.actuator import Actuator
from performancetest.core.cpu import CpuMonitor
from performancetest.core.device import AndroidDevice, IosDevice
from performancetest.core.devicebattery import DeviceBatteryMonitor
from performancetest.core.fps import FPSMonitor
from performancetest.core.network import NetworkMonitor
from performancetest.core.global_data import GlobalData as G, logger
from performancetest.core.gpu import GpuMonitor
from performancetest.core.iosperf import IosPerfMonitor
from performancetest.core.memory import MemoryMonitor
from performancetest.core.snapshot import SnapshotMonitor, IosSibSnapshotMonitor
from performancetest.web.dao import connect, Task


class TaskHandle(Process, Actuator):

    def __init__(self, serialno: str, server_addr: list[str], package: str, save_dir: str, task_id: int,
                 device_platform: str):
        super(TaskHandle, self).__init__()
        self.serialno = serialno
        self.server_addr = server_addr
        self.package = package
        self.save_dir = save_dir
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
        self.daemon = True
        self.task_id = task_id
        self.device_platform = device_platform  # ios | android

    def start(self):
        logger.info("join task handle")
        super().start()

    def run(self):
        logger.info("join task handle run")
        with connect() as session:
            current_task_running = session.query(Task).filter(
                Task.id == self.task_id).first()
            if current_task_running:
                current_task_running.status = 1
                current_task_running.pid = self.pid
            else:
                raise Exception("任务不存在")
            if self.device_platform == "android":
                try:
                    G.device = AndroidDevice(serialno=self.serialno, server_addr=self.server_addr,
                                             package=self.package, save_dir=self.save_dir)
                    G.device.start_app()
                except:
                    traceback.print_exc()
                    current_task_running.status = -1
                    session.flush()
                    session.commit()
                    raise Exception("任务启动失败")
                time.sleep(0.1)
                CpuMonitor(os.path.join(self.save_dir, "cpu.csv")).start()
                MemoryMonitor(os.path.join(self.save_dir, "memory.csv")).start()
                FPSMonitor(os.path.join(self.save_dir, "fps.csv")).start()
                GpuMonitor(os.path.join(self.save_dir, "gpu.csv")).start()
                DeviceBatteryMonitor(os.path.join(self.save_dir, "devicebattery.csv")).start()
                NetworkMonitor(os.path.join(self.save_dir, "network.csv")).start()
                SnapshotMonitor(os.path.join(self.save_dir, "picture_log"), self.serialno, self.server_addr).start()
            elif self.device_platform == "ios":
                try:
                    G.device = IosDevice(serialno=self.serialno, device_addr=self.server_addr,
                                         package=self.package, save_dir=self.save_dir)
                    G.device.start_app()
                except:
                    traceback.print_exc()
                    current_task_running.status = -1
                    current_task_running.end_time = datetime.datetime.now()
                    session.flush()
                    session.commit()
                    raise Exception("任务启动失败")
                IosPerfMonitor(save_dir=self.save_dir, G=G).start()
                IosSibSnapshotMonitor(os.path.join(self.save_dir, "picture_log"), G.device, self.package).start()

    def stop(self):
        G.stop_event.clear()

    def suspend(self):
        G.suspend_event.clear()


if __name__ == '__main__':
    task_process = TaskHandle(serialno="127.0.0.1:62001", server_addr=["localhost", 5037],
                              package="com.wxbz.nativeh5.yzcw.yeshen", save_dir="localhost", task_id=1, device_platform="android")
    task_process.start()
    time.sleep(2 * 10)
    task_process = TaskHandle(serialno="00008110-0012148E1E8B801E", server_addr=["10.131.129.128", 9123],
                              package="com.netease.id5", save_dir="localhost", task_id=1, device_platform="ios")
    task_process.start()
    time.sleep(2 * 10)
