#!/usr/bin/python
# -*- coding: UTF-8 -*-

import getpass
import os
import win32com.client


def get_qmt_exec_path() -> str:
    """
    获取QMT安装路径
    """
    username = getpass.getuser()  # 当前用户名
    qmt_exec_lnk = rf'C:\Users\{username}\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\国金证券QMT交易端\启动国金证券QMT交易端.lnk'
    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortCut(qmt_exec_lnk)
    # print(shortcut.Targetpath)
    target_path = str(shortcut.Targetpath)
    paths = target_path.split(r'\bin.x64')
    exec_path = os.path.expanduser(paths[0])
    exec_path = exec_path.replace('\\', '/')
    return exec_path


if __name__ == '__main__':
    path = get_qmt_exec_path()
    print(path)
