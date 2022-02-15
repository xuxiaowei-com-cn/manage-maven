# -*- coding:utf-8 -*-
import ctypes
import tkinter.messagebox
from tkinter.filedialog import askdirectory


class ManageMaven:
    """
    管理 Maven
    """

    def __init__(self):
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

    def askdirectory_command(self):
        """
        打开文件夹
        :return:
        """
        ask_directory = askdirectory()

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
