import os
import sys
import requests
import zipfile
from lxml import html
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QComboBox, QRadioButton, QTreeWidget, QTreeWidgetItem, QProgressBar, QMessageBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal


# 我的世界Java版版本列表
MC_VERSIONS = [
    "1.21.4", "1.21.3", "1.21.2", "1.21.1", "1.21", "1.20.6", "1.20.5", "1.20.4", "1.20.3", "1.20.2", "1.20.1", "1.20",
    "1.19.4", "1.19.3", "1.19.2", "1.19.1", "1.19", "1.18.2", "1.18.1", "1.18", "1.17.1", "1.17", "1.16.5", "1.16.4",
    "1.16.3", "1.16.2", "1.16.1", "1.16", "1.15.2", "1.15.1", "1.15", "1.14.4", "1.14.3", "1.14.2", "1.14.1", "1.14",
    "1.13.2", "1.13.1", "1.13", "1.12.2", "1.12.1", "1.12", "1.11.2", "1.11.1", "1.11", "1.10.2", "1.10.1", "1.10",
    "1.9.4", "1.9.3", "1.9.2", "1.9.1", "1.9", "1.8.9", "1.8.8", "1.8.7", "1.8.6", "1.8.5", "1.8.4", "1.8.3", "1.8.2",
    "1.8.1", "1.8", "1.7.10"
]

# 下载目录
DOWNLOAD_DIR = os.path.expanduser("~/downloads")
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)


class DownloadThread(QThread):
    """下载线程"""
    progress_signal = pyqtSignal(int)  # 进度信号
    finished_signal = pyqtSignal()  # 完成信号

    def __init__(self, selected_items, version, loader):
        super().__init__()
        self.selected_items = selected_items
        self.version = version
        self.loader = loader

    def run(self):
        """线程运行逻辑"""
        total = len(self.selected_items)
        for index, item in enumerate(self.selected_items):
            shader_name = item.text(0)
            self.download_shader(shader_name, self.version, self.loader)
            self.progress_signal.emit(int((index + 1) / total * 100))  # 更新进度

        self.finished_signal.emit()  # 下载完成

    def download_shader(self, shader_name, version, loader):
        """下载单个资源包"""
        shader_url = f"https://modrinth.com/shader/{shader_name}/versions?g={version}&l={loader}"
        try:
            response = requests.get(shader_url)
            response.raise_for_status()
            tree = html.fromstring(response.content)
            download_link = tree.xpath('//*[@id="__nuxt"]/div[4]/main/div[5]/div[6]/div[3]/section/div[2]/div[3]/div[2]/div[1]/a')[0].attrib["href"]
            print(f"Downloading {shader_name} from {download_link}")  # 打印下载链接
            file_path = os.path.join(DOWNLOAD_DIR, f"{shader_name}.zip")

            with requests.get(download_link, stream=True) as r:
                r.raise_for_status()
                with open(file_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)

            print(f"Downloaded {shader_name} to {file_path}")  # 打印下载完成信息

        except requests.exceptions.RequestException as e:
            print(f"Failed to download {shader_name}: {e}")  # 打印错误信息


class ShaderDownloaderApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("光影下载器")
        self.setGeometry(100, 100, 800, 600)

        # 主布局
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.layout = QVBoxLayout(self.main_widget)

        # 搜索栏
        self.search_layout = QHBoxLayout()
        self.search_input = QLineEdit(self)
        self.search_input.setPlaceholderText("光影名称")
        self.search_button = QPushButton("搜索", self)
        self.search_layout.addWidget(self.search_input)
        self.search_layout.addWidget(self.search_button)
        self.layout.addLayout(self.search_layout)

        # 分页输入栏
        self.page_layout = QHBoxLayout()
        self.page_label = QLabel("页码:", self)
        self.page_input = QLineEdit(self)
        self.page_input.setPlaceholderText("输入数字")
        self.load_page_button = QPushButton("加载该页", self)
        self.page_layout.addWidget(self.page_label)
        self.page_layout.addWidget(self.page_input)
        self.page_layout.addWidget(self.load_page_button)
        self.layout.addLayout(self.page_layout)

        # 版本选择器
        self.version_layout = QHBoxLayout()
        self.version_label = QLabel("MC版本:", self)
        self.version_combobox = QComboBox(self)
        self.version_combobox.addItems(MC_VERSIONS)
        self.version_layout.addWidget(self.version_label)
        self.version_layout.addWidget(self.version_combobox)
        self.layout.addLayout(self.version_layout)

        # 加载器选择
        self.loader_layout = QHBoxLayout()
        self.loader_label = QLabel("加载器:", self)
        self.iris_radio = QRadioButton("Iris", self)
        self.optifine_radio = QRadioButton("Optifine", self)
        self.iris_radio.setChecked(True)  # 默认选择Iris
        self.loader_layout.addWidget(self.loader_label)
        self.loader_layout.addWidget(self.iris_radio)
        self.loader_layout.addWidget(self.optifine_radio)
        self.layout.addLayout(self.loader_layout)

        # 资源包列表
        self.resource_list = QTreeWidget(self)
        self.resource_list.setHeaderLabel("搜索结果")
        self.resource_list.setSelectionMode(QTreeWidget.MultiSelection)
        self.layout.addWidget(self.resource_list)

        # 下载按钮和进度条
        self.download_layout = QHBoxLayout()
        self.download_button = QPushButton("下载指定光影包", self)
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setVisible(False)
        self.download_layout.addWidget(self.download_button)
        self.download_layout.addWidget(self.progress_bar)
        self.layout.addLayout(self.download_layout)

        # 连接信号和槽
        self.search_button.clicked.connect(self.on_search)
        self.load_page_button.clicked.connect(self.on_load_page)
        self.download_button.clicked.connect(self.on_download)

    def on_search(self):
        """处理搜索按钮点击事件"""
        keyword = self.search_input.text().strip()
        self.load_data(keyword, 1)  # 默认加载第一页

    def on_load_page(self):
        """处理加载指定页数按钮点击事件"""
        keyword = self.search_input.text().strip()
        page_number = self.page_input.text().strip()

        if not page_number.isdigit():
            QMessageBox.warning(self, "错误", "输入一个有效的页码")
            return

        page_number = int(page_number)
        if page_number < 1:
            QMessageBox.warning(self, "错误", "页码必须大于0")
            return

        self.load_data(keyword, page_number)

    def load_data(self, keyword, page_number):
        """加载指定页数的数据"""
        version = self.version_combobox.currentText()
        loader = "iris" if self.iris_radio.isChecked() else "optifine"

        # 清空资源包列表
        self.resource_list.clear()

        # 构造搜索URL
        search_url = f"https://modrinth.com/shaders/?q={keyword}&page={page_number}" if keyword else f"https://modrinth.com/shaders/?page={page_number}"
        print(f"Search URL: {search_url}")  # 打印搜索URL

        try:
            # 发送搜索请求
            response = requests.get(search_url)
            response.raise_for_status()
            tree = html.fromstring(response.content)
            results = tree.xpath('//*[@id="search-results"]/article/div[1]/a')

            if not results:
                QMessageBox.information(self, "叮", "没找到包")
                return

            # 显示搜索结果
            for result in results:
                shader_name = result.attrib["href"].split("/")[-1]
                item = QTreeWidgetItem(self.resource_list)
                item.setText(0, shader_name)
                item.setCheckState(0, Qt.Unchecked)

        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "错误", f"搜索失败: {e}")

    def on_download(self):
        """处理下载按钮点击事件"""
        selected_items = self.resource_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "错误", "请选择至少一个选项")
            return

        version = self.version_combobox.currentText()
        loader = "iris" if self.iris_radio.isChecked() else "optifine"

        # 显示进度条
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        # 启动下载线程
        self.download_thread = DownloadThread(selected_items, version, loader)
        self.download_thread.progress_signal.connect(self.update_progress)
        self.download_thread.finished_signal.connect(self.on_download_finished)
        self.download_thread.start()

    def update_progress(self, value):
        """更新进度条"""
        self.progress_bar.setValue(value)

    def on_download_finished(self):
        """下载完成后的操作"""
        self.progress_bar.setVisible(False)
        QMessageBox.information(self, "下载成功", "所有包已下载完毕，如有丢失的包请检查该包是否支持选中的版本")
        self.pack_shaders(self.resource_list.selectedItems())

    def pack_shaders(self, selected_items):
        """打包下载的资源包"""
        zip_name = f"{selected_items[0].text(0)}.zip"
        zip_path = os.path.join(DOWNLOAD_DIR, zip_name)

        with zipfile.ZipFile(zip_path, "w") as zipf:
            for item in selected_items:
                shader_name = item.text(0)
                file_path = os.path.join(DOWNLOAD_DIR, f"{shader_name}.zip")
                if os.path.exists(file_path):
                    print(f"Adding {file_path} to {zip_path}")  # 打印打包信息
                    zipf.write(file_path, os.path.basename(file_path))
                else:
                    print(f"File {file_path} does not exist")  # 打印文件不存在信息


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ShaderDownloaderApp()
    window.show()
    sys.exit(app.exec_())