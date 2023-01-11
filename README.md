# Manage Maven

- 打包
    - -F
        - 创建一个单文件可执行文件
    - -w
        - 不提供控制台窗口
    - -i
        - FILE.ico
            - 将图标应用于Windows可执行文件
        - FILE.exe
            - 从exe中提取图标
        - FILE.icns
            - 将该图标应用于 Mac 上的应用程序包
    - -n
        - 打包文件名

    ```shell
    pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
    pip install PyInstaller
    pip install BeautifulSoup4
    # 获取软件版本相关文件
    pyi-grab_version python.exe file_version.txt
    # 修改上述文件 file_version.txt，然后进行打包
    PyInstaller -F -w -i static/favicon.ico manage_maven.py --version-file file_version.py -n manage_maven-v0.0.4.0.exe
    ```
