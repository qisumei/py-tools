# py-tools
这是一个用 Python 编写的小工具集合，主要用于闲暇时间消磨时间或解决一些日常小问题。所有工具均在 Python 3.9 到 3.12 环境下开发和测试。
***
# sky系列（需要管理员权限）
sky.py：单项读取mid文件，通过mido来读取音符，使用pynput来对光遇进程输入按键(mid音符范围是C4-C6)  
sky_txt.py：单项读取sky studio的json格式的txt文件，使用pynput来对光遇进程输入按键  
sky_mix.py：包含前俩个文件的功能（推荐版本，因为前俩个已经是上一个版本了，并且效果一言难尽🤣）
***
# 光影下载器（无需管理员权限）
- dwshader.py
- **功能**：从 Modrinth 网站搜索并下载 Minecraft 光影包。
- **安装依赖**：
  - 确保已安装 Python 3.9 或更高版本。
  - 安装所需依赖：
    ```bash
    pip install PyQt5 requests lxml
    ```
- **注意事项**：
  - 下载的文件默认保存在 `~/downloads` 目录下。
  - 可以从第24行处修改：
    ```python
    # 下载目录
    DOWNLOAD_DIR = os.path.expanduser("~/downloads")
    ```
***
# 文件同步工具（局域网或公网）
## dbf-c.py（客户端）
- **功能**：
  - 定期连接服务器，比较本地与服务器端指定文件的元数据（修改时间、文件大小），并在检测到更新时下载最新文件到本地。
- **用法**：
  ```bash
  python dbf-c.py --server <服务器地址> --port 9999 --dir ./client_files

* **参数说明**：

  * `--server`：服务器 IP 或域名（必填）。
  * `--port`：服务器端口，默认 `9999`。
  * `--dir`：本地保存目录，默认 `./client_files`，以脚本所在目录开始计算。
* **注意事项**：

  * 确保网络连通，且服务端脚本 dbf-s.py 已在对应地址和端口启动。
  * 同步的目标文件默认为 `database.db`，可在文件第13行`self.target_file = "database.db"` 处更改脚本中的文件名。
  * 客户端每秒检测一次更新，可修改 `time.sleep(1)` 调整间隔。
  * 默认连接超时时间 `5` 秒，可在 `s.settimeout(5)` 中调整。

## dbf-s.py（服务端）

* **功能**：

  * 使用 watchdog 监控目录下指定文件的创建与修改，维护文件元数据；响应客户端请求，发送文件元数据和文件内容。
* **用法**：

  ```bash
  python dbf-s.py --host 0.0.0.0 --port 9999 --dir ./server_files
  ```
* **参数说明**：

  * `--host`：绑定地址，默认 `0.0.0.0`。
  * `--port`：监听端口，默认 `9999`。
  * `--dir`：同步目录，默认 `./server_files`，以脚本所在目录开始计算。
* **安装依赖**：

  ```bash
  pip install watchdog
  ```
* **注意事项**：

  * 需确保对 `--dir` 指定目录有读写权限，并已创建指定文件（首次可手动放置）。
  * watchdog 监听文件系统事件，若目录内有大量文件或频繁变动，可能影响性能。
  * 在生产环境建议使用进程守护工具（如 `supervisor`、`systemd`）后台运行服务。
* **额外配置**:
   * 如果需要同步整个文件夹里的文件（通过遍历所有文件）则修改SyncHandler类为：
   ```bash
  class SyncHandler(FileSystemEventHandler):
    def __init__(self, root_dir, file_meta):
        self.root_dir = root_dir
        self.file_meta = file_meta
        self.init_file_meta()

    def init_file_meta(self):
        for root, _, files in os.walk(self.root_dir):
            for f in files:
                path = os.path.join(root, f)
                self._update_meta(path)

    def _update_meta(self, path):
        rel_path = os.path.relpath(path, self.root_dir)
        stat = os.stat(path)
        self.file_meta[rel_path] = {
            'mtime': stat.st_mtime,
            'size': stat.st_size
        }

    def on_modified(self, event):
        if not event.is_directory:
            self._update_meta(event.src_path)

    def on_created(self, event):
        if not event.is_directory:
            self._update_meta(event.src_path)
   ```


---

# 特别鸣谢

[ChatGPT](https://chatgpt.com)
[DeepSeek](https://chat.deepseek.com)
[菜鸟编程](https://www.runoob.com/)

## 结尾

这个小工具集合是我在闲暇时间编写的，主要用于学习和实践 Python 编程。虽然功能简单，但希望能为有需要的人提供一些便利。如果你有任何建议或想法，欢迎提交 Issue 或 Pull Request！

---

**Happy Coding!** 🚀

