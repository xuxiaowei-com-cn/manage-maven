# upload_maven

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
    PyInstaller -F -w -i static/favicon.ico manage_maven.py -n "Maven 管理"
    ```
