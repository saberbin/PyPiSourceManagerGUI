# -*- coding: UTF-8 -*-
'''
@Project ：PyPiSourceManagerGUI 
@File    ：PyPiSourceManagerGUI.py
@IDE     ：PyCharm 
@Author  ：NelsonWu
@Date    ：2024/10/17 15:04 
@Desc    ：
'''
import os
from typing import List, Dict, Any, Union
from dataclasses import dataclass, asdict
from pathlib import Path
import sys
import json
import subprocess
import logging
import logging.handlers
import tkinter as tk
from tkinter.messagebox import showinfo, showwarning, showerror


class Loger(object):
    LogLevel: Dict[str, int] = {
        "INFO": logging.INFO,
        "DEBUG": logging.DEBUG,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR
    }

    def __init__(self, log_file: Union[str, Path], log_level: str= "INFO", log_name: str= 'main', log_format: str=None) -> None:
        self.log_file = log_file
        self.log_level = Loger.LogLevel.get(log_level)
        self.log_name = log_name
        self.log_format = log_format

    @staticmethod
    def set_logger(
            log_file: Union[str, Path],
            log_level: int =logging.INFO,
            log_name: str ="main",
            log_format: str = '%(asctime)s - %(process)d-%(threadName)s - '
                                            '%(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s'
    ) -> logging.Logger:
        log_handle = logging.FileHandler(filename=log_file, mode='a', encoding="utf-8")
        formatter = logging.Formatter(log_format)
        log_handle.setFormatter(formatter)
        logger = logging.Logger(name=log_name, level=log_level)
        logger.addHandler(log_handle)
        return logger

    def get_logger(self) -> logging.Logger:
        if self.log_format is None:
            return self.set_logger(self.log_file, log_level=self.log_level, log_name=self.log_name)
        else:
            return self.set_logger(
                self.log_file,
                log_level=self.log_level,
                log_name=self.log_name,
                log_format=self.log_format)


@dataclass
class PyPiSource(object):
    """pip源数据类"""
    pypi: str = "https://pypi.org/simple"  # 官方源
    aliyun: str = "https://mirrors.aliyun.com/pypi/simple/"  # 阿里云
    tsinghua: str = "https://pypi.tuna.tsinghua.edu.cn/simple/"  # 清华大学
    ustc: str = "https://pypi.mirrors.ustc.edu.cn/simple/"  # 中国科学技术大学
    douban: str = "http://pypi.douban.com/simple/"  # 豆瓣
    tencent: str = "https://mirrors.cloud.tencent.com/pypi/simple"  # 腾讯云
    huaweicloud: str = "https://repo.huaweicloud.com/repository/pypi/simple/"  # 华为云
    hustunique: str = "http://pypi.hustunique.com/"  # 华中科技大学
    netease: str = "https://mirrors.163.com/pypi/simple/"  # 网易


class PyPiSourceManager(object):
    def __init__(self) -> None:
        self.__user_profile = self.get_userprofile()
        self.__user_profile_path = Path(self.__user_profile)
        self.pip_conf_path = self.get_pip_conf_path()
        self.pip_conf_file = self.pip_conf_path.joinpath("pip.ini")

    @staticmethod
    def get_userprofile() -> str:
        """get_userprofile 获取用户环境变量里面的USERPROFILE配置

        Returns:
            str: USERPROFILE配置
        """
        return os.environ.get("USERPROFILE")

    def get_pip_conf_path(self) -> Path:
        """get_pip_conf_path 拼接出pip配置文件存放路径
        Windows默认情况下是存放在C盘下userprofile的AppData的Roaming的pip目录下的

        Returns:
            Path: pip配置文件存放路径
        """
        return self.__user_profile_path.joinpath("AppData").joinpath("Roaming").joinpath("pip")

    def backup_pip_conf(self) -> Path:
        """backup_pip_conf
        在pip配置文件目录备份当前pip配置文件，即pip.ini，备份文件名称为：pip-backup.ini
        如果该备份文件已存在，则会备份当前的pip.ini覆盖掉原有的pip-backup.ini文件。

        Raises:
            RuntimeError: 如果pip.ini文件不存在则会抛出这个异常。
        """
        if self.pip_conf_file.exists():
            with self.pip_conf_file.open("r", encoding="utf-8") as f:
                pip_data = f.read()
            pip_backup_file = self.pip_conf_path.joinpath("pip-backup.ini")
            with pip_backup_file.open("w", encoding="utf-8") as f:
                f.write(pip_data)
            return pip_backup_file
        else:
            raise RuntimeError(f"{self.pip_conf_file} 文件不存在。")

    def change_pip_source_by_conf(self, pypi_source_url: str) -> None:
        """change_pip_source 修改pip文件
        默认的pip配置文件如下，修改会按照如下模板进行修改
[global]
index-url = https://mirrors.aliyun.com/pypi/simple/
        Args:
            pypi_source_url (str): pypi的url地址

        Raises:
            RuntimeError: 传入的pypi地址为空则会抛出异常
        """
        if pypi_source_url:
            if os.environ.get("PyPiSource_Program_env") == "test":
                pip_file = self.pip_conf_path.joinpath("test-pip.ini")
            else:
                pip_file = self.pip_conf_file
            with pip_file.open("w", encoding="utf-8") as f:
                f.write("[global]\n")
                f.write(f"index-url = {pypi_source_url}\n")
        else:
            raise RuntimeError(f"传入的pypi_source_url为空，该参数不允许为空。修改失败，请传入正确参数后重试。")

    @staticmethod
    def change_pip_source_by_cmd(pypi_source_url: str):
        command_args = ['pip', 'config', 'set', 'global.index-url', pypi_source_url]
        try:
            result = subprocess.run(
                command_args,
                shell=True,
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
                check=True
                )
            output = result.stdout.decode()
            if output.startswith("Writing to"):
                pass
            else:
                raise RuntimeError(f"write to pip conf file error.")
        except Exception as e:
            raise RuntimeError(e)


class PySourceManagerGUI(object):
    def __init__(self):
        # normal var
        self.pypi_source = PyPiSource()
        self.pypi_source_manager = PyPiSourceManager()
        self.work_path = Path.cwd()
        log_path = self.work_path.parent.joinpath("logs")
        program_log = log_path.joinpath(f"PyPiSourceManagerRunning.log")
        msg_log = log_path.joinpath("PyPiSourceManager.log")

        program_loger = Loger(program_log, log_name="pypiSourceManager")
        self.running_logger = program_loger.get_logger()

        msg_loger = Loger(msg_log, log_name="pypiSourceManHistory", log_format="%(asctime)s - %(message)s")
        self.msg_logger = msg_loger.get_logger()

        # main window
        self.window = tk.Tk()
        self.window.title("PyPi Source Manager")
        self.window.geometry("280x500")

        # config window menu
        menu = tk.Menu(self.window)
        submenu = tk.Menu(menu, tearoff=0)
        submenu.add_command(label="关于", command=self.show_program_info)
        submenu.add_command(label="导出所有pypi源", command=self.export_pypi_sources)
        submenu.add_command(label="关闭", command=self.window.quit)
        menu.add_cascade(label="选项", menu=submenu)
        self.window.config(menu=menu)

        # gui var
        self.source_option = tk.StringVar()  # 生成字符串变量
        self.source_option.set('shell')  # 初始化变量值

        # pip源修改方式功能区
        radio_frame = tk.LabelFrame(self.window, relief="groove", text="pip source修改方式")
        radio_frame.pack(fill="x", padx=20, pady=20)
        shell_radio = tk.Radiobutton(radio_frame, variable=self.source_option, value="shell", text="shell方式")
        shell_radio.grid(row=0, column=0)
        conf_file_radio = tk.Radiobutton(radio_frame, variable=self.source_option, value="conf", text="conf file方式")
        conf_file_radio.grid(row=0, column=1)

        # 修改pip源功能区
        source_frame = tk.LabelFrame(self.window, relief="groove", text="修改pip源")
        source_frame.pack(fill="x", padx=20, pady=20)

        pypi_button = self.create_button(source_frame, "PyPi", self.pypi_source.pypi)
        aliyun_button = self.create_button(source_frame, "阿里云", self.pypi_source.aliyun)
        tsinghua_button = self.create_button(source_frame, "清华大学", self.pypi_source.tsinghua)
        ustc_button = self.create_button(source_frame, "中国科学技术大学", self.pypi_source.ustc)
        douban_button = self.create_button(source_frame, "豆瓣", self.pypi_source.douban)
        tencent_button = self.create_button(source_frame, "腾讯云", self.pypi_source.tencent)
        huaweicloud_button = self.create_button(source_frame, "华为云", self.pypi_source.huaweicloud)
        hustunique_button = self.create_button(source_frame, "华中科技大学", self.pypi_source.hustunique)
        netease_button = self.create_button(source_frame, "网易", self.pypi_source.netease)

        pypi_button.grid(row=0, column=0, padx=5, pady=5)
        aliyun_button.grid(row=0, column=1, padx=5, pady=5)
        tsinghua_button.grid(row=1, column=0, padx=5, pady=5)
        ustc_button.grid(row=1, column=1, padx=5, pady=5)
        douban_button.grid(row=2, column=0, padx=5, pady=5)
        tencent_button.grid(row=2, column=1, padx=5, pady=5)
        huaweicloud_button.grid(row=3, column=0, padx=5, pady=5)
        hustunique_button.grid(row=3, column=1, padx=5, pady=5)
        netease_button.grid(row=4, column=0, padx=5, pady=5)

        # 其他功能区控件与布局
        other_frame = tk.LabelFrame(self.window, text="其他", relief="groove")
        other_frame.pack(fill="x", padx=20, pady=20)
        # 备份pip文件的按钮
        backup_button = tk.Button(other_frame, text="备份pip配置文件", width=14, command=self.backup_pip_conf)
        backup_button.grid(row=0, column=0, padx=5, pady=5)
        # 打开pip文件按钮
        open_pip_file_button = tk.Button(other_frame, text="打开pip配置文件", width=14, command=self.open_pip_file)
        open_pip_file_button.grid(row=0, column=1, padx=5, pady=5)
        # 关闭主窗口按钮
        exit_button = tk.Button(other_frame, text="exit", width=14, command=self.window.quit)
        exit_button.grid(row=1, column=0, padx=5, pady=5)

    @staticmethod
    def show_program_info() -> None:
        """展示关于程序信息的方法"""
        msg = """此程序是基于Python的Tkinter开发关于修改pip源的GUI程序。
供所有用户免费使用与学习。
github地址：https://github.com/saberbin/PyPiSourceManagerGUI.git"""
        showinfo(title="PyPiSourceManager", message=msg)

    def export_pypi_sources(self) -> None:
        """
        将pip源的数据类序列化成json数据并写入Windows剪贴板中
        :return: None
        """
        pypi_source_dict = asdict(self.pypi_source)
        self.window.clipboard_append(json.dumps(pypi_source_dict))
        self.window.update()  # 更新剪贴板内容
        self.window.after(100)  # 等待100毫秒，确保剪贴板更新
        self.msg_logger.info("pip源数据写入剪切板")

    def create_button(self, window, text, pypi_source_url, width=14) -> tk.Button:
        """create_button 创建修改pip源frame的按钮控件
        因为tk.Button方法创建会导致代码过长，这里为了代码美观与可读性封装成方法
        Args:
            window (tk.Tk, tk.Frame): 窗口或者frame对象，这里应该默认为“修改pip源”的frame
            text (str): 按钮控件显示内容
            pypi_source_url (str): pip源url路径
            width (int, optional): 按钮控件宽度 Defaults to 14.

        Returns:
            tk.Button: 修改pip源的按钮控件对象
        """
        button = tk.Button(
            window,
            text=text,
            command=lambda: self.change_pip_source(pypi_source_url),
            width=width
        )
        return button

    def backup_pip_conf(self) -> None:
        """backup_pip_conf 备份pip配置文件

        Raises:
            RuntimeError: 配置文件如果不存在则会抛出异常
        """
        try:
            pip_backup_file: Path = self.pypi_source_manager.backup_pip_conf()
            showinfo(title="执行成功", message=f"pip配置文件备份成功，备份位置：{pip_backup_file}")
            self.msg_logger.info(f"pip配置文件备份成功，备份位置：{pip_backup_file}")
        except Exception as e:
            self.running_logger.error("pip配置文件备份失败")
            raise RuntimeError(e)

    def open_pip_file(self) -> None:
        """
        调用Windows系统下默认程序打开pip.ini文件
        :return:
        """
        pip_file: Path = self.pypi_source_manager.pip_conf_file
        if pip_file.exists():
            os.startfile(pip_file)
        else:
            self.msg_logger.error(f"pip配置文件不存在，无法调用程序打开该文件。{pip_file} ")
            RuntimeError(f"pip配置文件不存在,{pip_file}")

    def change_pip_source(self, pypi_source_url: str):
        """change_pip_source 修改pip源的方法
        通过单选按钮切换修改方式，shell或者conf。
        shell方法则是通过调用终端执行命令的方式去修改
        conf方法则是直接覆盖原有的pip配置文件
        Args:
            pypi_source_url (str): pip源url地址

        Raises:
            RuntimeError: _description_
        """
        source_change_option = self.source_option.get()
        try:
            if source_change_option == "shell":
                self.pypi_source_manager.change_pip_source_by_cmd(pypi_source_url)
                self.msg_logger.info(f"通过命令方式修改pip源成功，修改后的pip源为：{pypi_source_url}")
            elif source_change_option == "conf":
                self.pypi_source_manager.change_pip_source_by_conf(pypi_source_url)
                self.msg_logger.info(f"通过配置文件方式修改pip源成功，修改后的pip源为：{pypi_source_url}")
            showinfo(title="执行成功", message=f"修改pip源成功，修改后的pip源为：{pypi_source_url}")
        except Exception as e:
            self.running_logger.error(f"修改pip源失败，具体原因: {e}")
            # raise RuntimeError(f"修改pip源失败，具体原因: {e}")
            showerror(title="发生错误", message=f"修改pip源失败，具体原因: {e}")

    def run(self) -> None:
        """run PyPiSourceManagerGUI的启动方法"""
        try:
            self.window.mainloop()
        except Exception as e:
            self.running_logger.error(e)


if __name__ == '__main__':
    main_gui = PySourceManagerGUI()
    main_gui.run()
