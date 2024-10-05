import sys
import subprocess
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
                             QListWidget, QLabel, QFrame, QColorDialog, QPushButton, 
                             QDialog, QLineEdit, QListWidgetItem, QMenu, QInputDialog, 
                             QMessageBox, QScrollArea, QGridLayout)
from PyQt6.QtGui import QColor
from PyQt6.QtCore import Qt, QSize

import json
import os

# 这个类用于创建一个对话框，允许用户添加新的笔记，包括输入笔记名称和选择颜色。
class AddNoteDialog(QDialog):
    def __init__(self, parent=None): # 初始化对话框，设置窗口标题和大小，并创建一个垂直布局
        super().__init__(parent)
        self.setWindowTitle("添加新笔记")
        self.setFixedSize(400, 300)
        self.layout = QVBoxLayout(self) # 创建一个垂直布局，并将其设置为对话框的布局
        self.color_blocks = []  # 用于存储用户选择的颜色块

        # 笔记名称输入框
        self.note_name_input = QLineEdit(self) # 创建一个QLineEdit控件，用于输入笔记名称
        self.note_name_input.setPlaceholderText("输入笔记名称") # 设置输入框的占位符文本为“输入笔记名称”
        self.layout.addWidget(self.note_name_input) # 将输入框添加到布局中

        # 颜色显示区域
        self.color_display = QWidget() # 创建一个QWidget控件，用于显示颜色
        self.color_display.setFixedSize(200, 100) # 设置颜色显示区域的大小
        self.color_display.setStyleSheet("background-color: white; border: 1px solid gray;") # 设置颜色显示区域的样式
        self.color_layout = QHBoxLayout(self.color_display) # 创建一个水平布局，并将其设置为颜色显示区域的布局
        self.layout.addWidget(self.color_display, alignment=Qt.AlignmentFlag.AlignCenter) # 将颜色显示区域添加到布局中，并将其居中对齐

        # 颜色代码输入框
        self.color_input = QLineEdit(self)# 创建一个QLineEdit控件，用于输入颜色代码
        self.color_input.setPlaceholderText("输入颜色代码 (例如: #FF0000)") # 设置输入框的占位符文本为“输入颜色代码 (例如: #FF0000)”
        self.layout.addWidget(self.color_input) # 将输入框添加到布局中

        # 按钮布局
        button_layout = QHBoxLayout() # 创建一个水平布局，用于放置按钮
        self.add_button = QPushButton("添加") # 创建一个QPushButton控件，用于添加颜色
        self.add_button.clicked.connect(self.add_color) # 将添加颜色按钮的点击事件连接到add_color方法
        self.complete_button = QPushButton("完成") # 创建一个QPushButton控件，用于完成添加
        self.complete_button.clicked.connect(self.accept) # 将完成按钮的点击事件连接到accept方法
        button_layout.addWidget(self.add_button) # 将添加按钮添加到布局中
        button_layout.addWidget(self.complete_button) # 将完成按钮添加到布局中
        self.layout.addLayout(button_layout) # 将按钮布局添加到布局中

    def add_color(self): # 添加颜色 
        color_code = self.color_input.text() # 获取颜色代码，从输入框获取
        if color_code.startswith('#') and len(color_code) == 7: # 如果颜色代码以#开头，并且长度为7
            color_block = QLabel() # 创建一个QLabel控件，用于显示颜色
            color_block.setFixedSize(30, 30) # 设置颜色块的大小
            color_block.setStyleSheet(f"background-color: {color_code}; border: 1px solid black;") # 设置颜色块的样式
            self.color_layout.addWidget(color_block) # 将颜色块添加到颜色布局中
            self.color_blocks.append(color_code) # 将颜色代码添加到颜色块列表中
            self.color_input.clear() # 清空颜色输入框
        else:
            QMessageBox.warning(self, "错误", "请输入有效的颜色代码 (例如: #FF0000)")

    def get_note_data(self): # 获取笔记数据
        return self.note_name_input.text(), self.color_blocks # 返回笔记名称和颜色块列表

class NoteListItem(QWidget): # 笔记列表项
    def __init__(self, note_name, colors): # 初始化笔记列表项，设置布局，设置内容边距，设置笔记名称和颜色数量
        super().__init__()
        layout = QHBoxLayout(self) # 创建一个水平布局，并将其设置为笔记列表项的布局
        layout.setContentsMargins(5, 5, 5, 5) # 设置布局的边距

        # 显示笔记名称和颜色数量
        name_label = QLabel(f"{note_name} ({len(colors)} 颜色)") # 创建一个QLabel控件，用于显示笔记名称和颜色数量
        layout.addWidget(name_label) # 将笔记名称和颜色数量添加到布局中

        # 添加一些间距
        layout.addSpacing(10)

        # 显示颜色方块
        for color in colors[:5]:  # 只显示前5个颜色，防止项目过长
            color_label = QLabel()
            color_label.setFixedSize(20, 20)
            color_label.setStyleSheet(f"background-color: {color}; border: 1px solid black;")
            layout.addWidget(color_label)

        # 如果颜色超过5个，显示省略号
        if len(colors) > 5:
            more_label = QLabel("...")
            layout.addWidget(more_label)

        layout.addStretch() # 添加一个伸缩空间，用于在布局中添加额外的空间

    def sizeHint(self): # 返回一个QSize对象，用于设置笔记列表项的大小
        return QSize(300, 40)  # 稍微增加宽度以适应更多内容

class NoteDetailDialog(QDialog): # 笔记详情对话框
    def __init__(self, note_name, colors, parent=None): # 初始化笔记详情对话框，设置窗口标题，设置最小大小，设置布局
        super().__init__(parent)
        self.setWindowTitle(f"笔记详情: {note_name}")
        self.setMinimumSize(500, 400)  # 稍微增加了窗口大小
        
        layout = QVBoxLayout(self)
        
        # 显示笔记名称
        name_label = QLabel(f"笔记名称: {note_name}")
        layout.addWidget(name_label)
        
        # 显示颜色数量
        color_count_label = QLabel(f"颜色数量: {len(colors)}")
        layout.addWidget(color_count_label)
        
        # 创建一个滚动区域来显示所有颜色
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        
        # 显示所有颜色及其编码
        for color in colors:
            color_widget = QWidget()
            color_layout = QHBoxLayout(color_widget)
            
            # 颜色预览
            color_preview = QLabel()
            color_preview.setFixedSize(50, 50)
            color_preview.setStyleSheet(f"background-color: {color}; border: 1px solid black;")
            color_layout.addWidget(color_preview)
            
            # 颜色编码
            color_code_label = QLabel(color)
            color_layout.addWidget(color_code_label)
            
            color_layout.addStretch()
            scroll_layout.addWidget(color_widget)
        
        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)
        
        # 添加关闭按钮
        close_button = QPushButton("关闭")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.notes_data = []
        self.init_ui()
        self.load_notes()
        self.note_list.setStyleSheet("QListWidget::item { border-bottom: 1px solid #ddd; }")
        self.note_list.setSpacing(2)

    def init_ui(self):
        self.setWindowTitle("颜色管理器")
        # 设置窗口的位置和大小
        # setGeometry(x, y, width, height)
        # x: 窗口左上角的水平位置，单位为像素
        # y: 窗口左上角的垂直位置，单位为像素
        # width: 窗口的宽度，单位为像素
        # height: 窗口的高度，单位为像素
        self.setGeometry(100, 100, 500, 300)  # 设置窗口的位置和大小
        
        # 设置窗口的最小和最大大小
        self.setMinimumSize(400, 300)  # 最小大小
        self.setMaximumSize(1200, 800)  # 最大大小

        # 主布局
        main_layout = QHBoxLayout()

        # 左侧颜色选择器
        self.color_selection_widget = self.create_color_selection_widget()
        main_layout.addWidget(self.color_selection_widget)

        # 右侧笔记列表
        note_list_widget = self.create_note_list_widget()
        main_layout.addWidget(note_list_widget)

        # 设置主窗口的中心部件
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # 连接右键菜单
        self.note_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu) # 设置右键菜单策略为自定义右键菜单
        self.note_list.customContextMenuRequested.connect(self.show_context_menu) # 连接右键菜单事件

        # 连接双击事件
        self.note_list.itemDoubleClicked.connect(self.show_note_detail) # 连接双击事件

    def create_color_selection_widget(self):
        widget = QFrame() # 创建一个QFrame控件，用于显示颜色选择器
        widget.setFrameShape(QFrame.Shape.StyledPanel) # 设置QFrame的形状为样式面板
        layout = QVBoxLayout() # 创建一个垂直布局，并将其设置为颜色选择器的布局

        # 颜色显示区
        self.color_display = QLabel() # 创建一个QLabel控件，用于显示颜色
        self.color_display.setFixedSize(150, 150)  # 这里设置颜色显示区的大小
        self.color_display.setStyleSheet("background-color: white; border: 1px solid black;") # 设置颜色显示区的样式
        layout.addWidget(self.color_display, alignment=Qt.AlignmentFlag.AlignCenter) # 将颜色显示区添加到布局中，并将其居中对齐

        # 水平布局：输入框和颜色选择按钮
        input_layout = QHBoxLayout() # 创建一个水平布局，并将其设置为输入框和颜色选择按钮的布局

        self.color_input = QLineEdit() # 创建一个QLineEdit控件，用于输入颜色代码
        self.color_input.setPlaceholderText("代码(#FF0000)")
        self.color_input.textChanged.connect(self.update_color_display) # 连接颜色输入框的文本变化事件
        input_layout.addWidget(self.color_input) # 将颜色输入框添加到布局中

        select_color_button = QPushButton("选择颜色") # 创建一个QPushButton控件，用于选择颜色
        select_color_button.clicked.connect(self.open_kivy_color_picker) # 连接颜色选择按钮的点击事件
        input_layout.addWidget(select_color_button) # 将颜色选择按钮添加到布局中

        layout.addLayout(input_layout) # 将输入框和颜色选择按钮的布局添加到布局中

        widget.setLayout(layout) # 将布局添加到颜色选择器中
        return widget # 返回颜色选择器

    def update_color_display(self): # 更新颜色显示区
        color_code = self.color_input.text() # 获取颜色代码
        if color_code.startswith('#') and len(color_code) == 7: # 如果颜色代码以#开头，并且长度为7
            self.color_display.setStyleSheet(f"background-color: {color_code}; border: 1px solid black;") # 设置颜色显示区的样式
        else:
            self.color_display.setStyleSheet("background-color: white; border: 1px solid black;") # 设置颜色显示区的样式

    def open_kivy_color_picker(self): # 打开kivy颜色选择器
        current_dir = os.path.dirname(os.path.abspath(__file__)) # 获取当前文件的目录
        kivy_picker_path = os.path.join(current_dir, "kivy_color_picker.py") # 获取kivy颜色选择器的路径
        subprocess.run(["python", kivy_picker_path], check=True) # 运行kivy颜色选择器
        
        selected_color_path = os.path.join(current_dir, "selected_color.txt") # 获取选中的颜色路径
        if os.path.exists(selected_color_path): # 如果选中的颜色路径存在
            with open(selected_color_path, 'r') as f: #with上下文管理器，打开选中的颜色路径
                color = f.read().strip() # 读取选中的颜色
            self.color_input.setText(color) # 设置颜色输入框的文本
            self.update_color_display() # 更新颜色显示区
            os.remove(selected_color_path) # 删除选中的颜色路径
        else:
            print("Color selection file not found.") # 如果选中的颜色路径不存在，打印错误信息

    def create_note_list_widget(self): # 创建笔记列表
        widget = QFrame() # 创建一个QFrame控件，用于显示笔记列表
        widget.setFrameShape(QFrame.Shape.StyledPanel) # 设置QFrame的形状为样式面板
        layout = QVBoxLayout() # 创建一个垂直布局，并将其设置为笔记列表的布局

        # 标题和添加按钮的水平布局
        title_layout = QHBoxLayout() # 创建一个水平布局，并将其设置为标题和添加按钮的布局
        label = QLabel("笔记列表") # 创建一个QLabel控件，用于显示标题
        title_layout.addWidget(label) # 将标题添加到布局中
        
        add_button = QPushButton("+") # 创建一个QPushButton控件，用于添加笔记
        add_button.setFixedSize(30, 30) # 设置添加按钮的大小
        add_button.clicked.connect(self.add_new_note) # 连接添加按钮的点击事件
        title_layout.addWidget(add_button, alignment=Qt.AlignmentFlag.AlignRight) # 将添加按钮添加到布局中，并将其右对齐

        layout.addLayout(title_layout) # 将标题和添加按钮的布局添加到布局中

        self.note_list = QListWidget() # 创建一个QListWidget控件，用于显示笔记列表
        layout.addWidget(self.note_list) # 将笔记列表添加到布局中

        widget.setLayout(layout) # 将布局添加到笔记列表中
        return widget # 返回笔记列表

    def add_new_note(self): # 添加新笔记
        dialog = AddNoteDialog(self) # 创建一个AddNoteDialog对话框
        if dialog.exec() == QDialog.DialogCode.Accepted: # 如果对话框被接受
            note_name, colors = dialog.get_note_data() # 获取笔记名称和颜色
            if note_name and colors: # 如果笔记名称和颜色不为空
                note_data = {"name": note_name, "colors": colors} # 创建一个字典，用于存储笔记名称和颜色
                self.notes_data.append(note_data) # 将笔记数据添加到笔记数据列表中
                self.update_note_list() # 更新笔记列表
                self.save_notes() # 保存笔记数据

    def update_note_list(self): # 更新笔记列表
        self.note_list.clear() # 清空笔记列表
        for note in self.notes_data: # 遍历笔记数据列表
            item = QListWidgetItem(self.note_list) # 创建一个QListWidgetItem控件，用于显示笔记
            note_widget = NoteListItem(note['name'], note['colors']) # 创建一个NoteListItem控件，用于显示笔记
            item.setSizeHint(note_widget.sizeHint()) # 设置笔记的大小
            self.note_list.addItem(item) # 将笔记添加到笔记列表中
            self.note_list.setItemWidget(item, note_widget) # 将笔记添加到笔记列表中

    def save_notes(self): # 保存笔记数据
        with open("notes_data.json", "w") as f: # 打开notes_data.json文件
            json.dump(self.notes_data, f) # 将笔记数据保存到notes_data.json文件中

    def load_notes(self): # 加载笔记数据
        if os.path.exists("notes_data.json"): # 如果notes_data.json文件存在
            with open("notes_data.json", "r") as f: # 打开notes_data.json文件
                self.notes_data = json.load(f) # 将笔记数据加载到notes_data.json文件中
            self.update_note_list() # 更新笔记列表

    def show_context_menu(self, position): # 显示右键菜单
        menu = QMenu() # 创建一个QMenu控件，用于显示右键菜单
        rename_action = menu.addAction("重命名") # 创建一个QAction控件，用于重命名
        delete_action = menu.addAction("删除") # 创建一个QAction控件，用于删除

        action = menu.exec(self.note_list.mapToGlobal(position)) # 显示右键菜单
        
        if action == rename_action: # 如果点击了重命名
            self.rename_note() # 重命名笔记
        elif action == delete_action: # 如果点击了删除
            self.delete_note() # 删除笔记

    def rename_note(self): # 重命名笔记
        current_item = self.note_list.currentItem() # 获取当前选中的笔记
        if current_item: # 如果当前选中的笔记不为空
            current_index = self.note_list.row(current_item) # 获取当前选中的笔记的索引
            old_name = self.notes_data[current_index]['name'] # 获取当前选中的笔记的名称
            new_name, ok = QInputDialog.getText(self, "重命名笔记", "输入新的笔记名称:", text=old_name) # 弹出一个输入对话框，用于输入新的笔记名称
            if ok and new_name: # 如果输入了新的笔记名称
                self.notes_data[current_index]['name'] = new_name # 将新的笔记名称保存到笔记数据列表中
                self.update_note_list() # 更新笔记列表
                self.save_notes() # 保存笔记数据

    def delete_note(self): # 删除笔记
        current_item = self.note_list.currentItem() # 获取当前选中的笔记
        if current_item: # 如果当前选中的笔记不为空
            reply = QMessageBox.question(self, '确认删除', # 弹出一个确认删除对话框
                                         "您确定要删除这个笔记吗？", 
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
                                         QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                current_index = self.note_list.row(current_item)
                del self.notes_data[current_index]
                self.update_note_list()
                self.save_notes()

    def show_note_detail(self, item): # 显示笔记详情
        index = self.note_list.row(item) # 获取当前选中的笔记的索引
        note = self.notes_data[index] # 获取当前选中的笔记的数据
        dialog = NoteDetailDialog(note['name'], note['colors'], self) # 创建一个NoteDetailDialog对话框
        dialog.exec() # 显示笔记详情对话框

if __name__ == "__main__": # 如果当前文件是主文件
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show() # 显示主窗口
    sys.exit(app.exec()) # 退出应用程序