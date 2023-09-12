# coding=utf-8
import subprocess
import traceback
from builtins import *

import airtest.core.android.adb
import requests

from performancetest.core.global_data import logger


def split_cmd(cmds):
    return cmds.split() if isinstance(cmds, str) else list(cmds)


def proc_communicate_timeout(proc, timeout):
    try:
        stdout, stderr = proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired as e:
        proc.kill()
        stdout, stderr = proc.communicate()
        exp = Exception("Command {cmd} timed out after {timeout} seconds: stdout['{stdout}'], "
                        "stderr['{stderr}']".format(cmd=proc.args, timeout=e.timeout,
                                                    stdout=stdout, stderr=stderr))
        raise (exp)

    return stdout, stderr


class ADB(object):
    def __init__(self, serialno=None, adb_path=None, server_addr=None):
        self.serialno = serialno
        self.adb_path = adb_path or airtest.core.android.adb.ADB.builtin_adb_path()
        self._set_cmd_options(server_addr)
        self.server_addr = server_addr

    def _set_cmd_options(self, server_addr=None):
        logger.info(server_addr)
        self.host = server_addr[0] if server_addr[0] else "127.0.0.1"
        self.port = server_addr[1] if server_addr[1] else 5037
        self.cmd_options = [self.adb_path]
        if self.host:
            self.cmd_options += ['-H', self.host]
        if self.port:
            self.cmd_options += ['-P', str(self.port)]

    def start_shell(self, cmds):
        """
        Handle `adb shell` c(s)

        Args:
            cmds: adb shell command(s)

        Returns:
            None

        """
        cmds = ['shell'] + split_cmd(cmds)
        return self.start_cmd(cmds)

    def start_cmd(self, cmds, device=True, only_args=False):
        """
        Start a subprocess with adb command(s)

        Args:
            cmds: command(s) to be run
            device: if True, the device serial number must be specified by `-s serialno` argument

        Raises:
            RuntimeError: if `device` is True and serialno is not specified

        Returns:
            a subprocess

        """
        if device:
            if not self.serialno:
                raise RuntimeError("please set serialno first")
            cmd_options = self.cmd_options + ['-s', self.serialno]
        else:
            cmd_options = self.cmd_options

        cmds = cmd_options + split_cmd(cmds)
        logger.debug(cmds)
        logger.debug(" ".join(cmds))
        if only_args:
            return cmds
        proc = subprocess.Popen(
            cmds,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=0
        )
        return proc

    def raw_shell(self, cmds, ensure_unicode=True):
        cmds = ['shell'] + split_cmd(cmds)
        logger.info("shell执行命令：{}".format(str(cmds)))
        out = self.cmd(cmds, ensure_unicode=False)
        return out

    def cmd(self, cmds, device=True, ensure_unicode=True, timeout=None):
        proc = self.start_cmd(cmds, device)
        if timeout:
            stdout, stderr = proc_communicate_timeout(proc, timeout)
        else:
            stdout, stderr = proc.communicate()
        logger.error(f"err msg {stderr}")
        return stdout

    def killpid(self, pid):
        logger.info("进入killpid函数")
        self.raw_shell("kill {}".format(pid))
        logger.info("killpid函数执行结束")
