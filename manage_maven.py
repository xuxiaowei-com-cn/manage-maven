# -*- coding:utf-8 -*-
import ctypes
import logging.handlers
import os
import time
import tkinter.messagebox
from tkinter.filedialog import askdirectory


class ManageMaven:
    """
    管理 Maven
    """

    def __log__(self):
        """日志配置"""

        self.FMT = "%(asctime)s - %(levelname)s - %(filename)s[:%(lineno)d] - %(message)s"

        # 日志文件夹
        self.LOGGING_DIRECTORY = os.path.join(os.getenv("APPDATA"), 'manage_maven', 'log',
                                              time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()))

        # 判断文件是否不存在
        if not os.path.exists(self.LOGGING_DIRECTORY):
            # 创建文件夹
            os.makedirs(self.LOGGING_DIRECTORY)

        # 获取日志记录器
        logger = logging.getLogger()
        # 日志等级
        logger.setLevel(logging.DEBUG)

        # 全部日志
        all_handler = logging.handlers.TimedRotatingFileHandler(os.path.join(self.LOGGING_DIRECTORY, 'all.log'))
        all_handler.setFormatter(logging.Formatter(self.FMT))
        logger.addHandler(all_handler)

        # 正常日志
        into_handler = logging.handlers.TimedRotatingFileHandler(os.path.join(self.LOGGING_DIRECTORY, 'info.log'))
        into_handler.setLevel(logging.INFO)
        into_handler.setFormatter(logging.Formatter(self.FMT))
        logger.addHandler(into_handler)

        # 异常日志
        error_handler = logging.FileHandler(os.path.join(self.LOGGING_DIRECTORY, 'error.log'))
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(logging.Formatter(self.FMT))
        logger.addHandler(error_handler)

        # 创建一个日志处理程序，用于将日志输出到控制台
        sh = logging.StreamHandler()
        # 设置输出到控制台的日志等级
        sh.setLevel(logging.DEBUG)
        # 添加处理程序
        logger.addHandler(sh)

    def __init__(self):
        """
        初始化
        """
        self.__log__()

        self.root = tkinter.Tk()
        self.root.title("管理 Maven")

        # 窗口大小
        width = 800
        height = 600

        x = self.root.winfo_screenwidth() / 2 - width / 2
        # 空出任务栏高度
        y = (self.root.winfo_screenheight() - 50) / 2 - height / 2

        # 设置窗口的大小与位置
        # self.root.geometry("800x600+368+107")
        self.root.geometry('%dx%d+%d+%d' % (width, height, x, y))

        # 创建一个Canvas
        # 设置其背景色为白色：bg='white'
        self.cv = tkinter.Canvas(self.root)

        # 上传文件夹输入框
        self.askdirectory_entry = tkinter.Entry(self.root)
        self.askdirectory_entry.pack()

        # 上传文件夹选择按钮
        self.askdirectory_button = tkinter.Button(self.root, text="选择上传的文件夹", command=self.askdirectory_command)
        self.askdirectory_button.pack()

        # 用户名输入框
        self.username_entry = tkinter.Entry(self.root)
        self.username_entry.pack()

        # 密码输入框
        self.password_entry = tkinter.Entry(self.root)
        self.password_entry.pack()

        # 上传按钮
        self.upload_button = tkinter.Button(self.root, text="上传文件", command=self.upload_command)
        self.upload_button.pack()

        logging.info('程序启动...')
        logging.debug(f'日志目录：{self.LOGGING_DIRECTORY}')

    def askdirectory_command(self):
        """
        打开文件夹
        :return:
        """
        ask_directory = askdirectory()
        logging.info(f'选择上传文件夹：{ask_directory}')

        if ask_directory != '':
            # 清空
            self.askdirectory_entry.delete(0, tkinter.END)
            # 将选择的文件夹放入文件夹输入框
            self.askdirectory_entry.insert(0, ask_directory)

    def upload_command(self):
        """
        上传
        :return:
        """
        # 0x00 到 0x06 为无图标弹窗
        ctypes.windll.user32.MessageBoxA(0, self.askdirectory_entry.get().encode('gbk'), "上传文件夹".encode('gbk'), 0x00)
        ctypes.windll.user32.MessageBoxA(0, self.username_entry.get().encode('gbk'), "用户名".encode('gbk'), 0x00)
        ctypes.windll.user32.MessageBoxA(0, self.password_entry.get().encode('gbk'), "密码".encode('gbk'), 0x00)


if __name__ == '__main__':
    ManageMaven().root.mainloop()
