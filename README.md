# py-tools
这是一个用 Python 编写的小工具集合，主要用于闲暇时间消磨时间或解决一些日常小问题。所有工具均在 Python 3.9 到 3.12 环境下开发和测试。
***
# sky系列（需要管理员权限）
sky.py：单项读取mid文件，通过mido来读取音符，使用pynput来对光遇进程输入按键(mid音符范围是C4-C6)\
\
sky_txt.py：单项读取sky studio的json格式的txt文件，使用pynput来对光遇进程输入按键\
\
sky_mix.py：包含前俩个文件的功能（推荐版本，因为前俩个已经是上一个版本了，并且效果一言难尽🤣）
***
# 光影下载器（无需管理员权限）
- dwshader.py
- **功能**：从 Modrinth 网站搜索并下载 Minecraft 光影包。
-  **安装依赖**：
   - 确保已安装 Python 3.9 或更高版本。
   - 安装所需依赖：
     ```bash
     pip install PyQt5 requests lxml
     ```
**注意事项**：
   - 下载的文件默认保存在 `~/downloads` 目录下。
   - 可以从第24行处修改：
     ```bash
     # 下载目录
      DOWNLOAD_DIR = os.path.expanduser("~/downloads")
     ```
# 特别鸣谢
[ChatGPT](https://chatgpt.com)\
[DeepSeek](https://chat.deepseek.com)
## 结尾

这个小工具集合是我在闲暇时间编写的，主要用于学习和实践 Python 编程。虽然功能简单，但希望能为有需要的人提供一些便利。如果你有任何建议或想法，欢迎提交 Issue 或 Pull Request！

---

**Happy Coding!** 🚀


