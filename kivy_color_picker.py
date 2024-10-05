from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.colorpicker import ColorPicker
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle
import os
"""
这是一个Kivy应用程序，用于选择颜色并将其保存到文件中。
"""
class OKButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.text = 'OK'
        self.background_normal = ''
        self.background_color = [0.3, 0.3, 0.3, 1]  # 深灰色背景
        self.color = [1, 1, 1, 1]  # 白色文字

class ColorPickerApp(App): # 颜色选择器应用程序
    def build(self):
        layout = BoxLayout(orientation='vertical') # 创建一个垂直布局
        self.color_picker = ColorPicker()
        layout.add_widget(self.color_picker)
        
        confirm_button = OKButton(size_hint=(1, 0.1))
        confirm_button.bind(on_press=self.on_select)
        layout.add_widget(confirm_button)
        
        return layout

    def on_select(self, instance): # 选择颜色后执行的函数
        color = self.color_picker.color # 获取颜色
        hex_color = "#{:02x}{:02x}{:02x}".format(int(color[0]*255), int(color[1]*255), int(color[2]*255)) # 将颜色转换为十六进制
        current_dir = os.path.dirname(os.path.abspath(__file__)) # 获取当前文件的目录
        with open(os.path.join(current_dir, 'selected_color.txt'), 'w') as f: # 将颜色写入文件
            f.write(hex_color)
        App.get_running_app().stop() # 停止应用程序

if __name__ == '__main__':
    """
    这是应用程序的入口点。
    如果当前文件是主文件，则运行应用程序。
    因为这个类继承了APP类，所以拥有了run（）方法
    """
    ColorPickerApp().run() # 运行应用程序