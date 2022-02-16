# -*- coding: utf-8 -*-
from distutils.core import setup

import py2exe

# 仅用于在格式化时，不删除 py2exe 导入，否则打包将出现异常：error: invalid command 'py2exe'
print(py2exe.version.__version__)

# 无CMD窗口
setup(
    options={
        "py2exe": {
            "bundle_files": 1,  # 捆绑文件
            "compressed": 1,  # 压缩
            "dist_dir": "dist-console",  # 打包文件夹
            "optimize": 2,  # 优化
        }
    },
    console=[
        {
            "script": "manage_maven.py",
            "icon_resources": [(1, "static/favicon.ico")],
            "description": "Maven 管理工具",
            "version": '0.0.0.1',
        }
    ]
)
