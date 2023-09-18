"""
Project: ak_sw_benchmarker Azure Kinect Size Estimation & Weight Prediction Benchmarker https://github.com/GRAP-UdL-AT/ak_sw_benchmarker/
Github repository: https://github.com/juancarlosmiranda/ak_video_analyser

Author: Juan Carlos Miranda
* https://juancarlosmiranda.github.io/
* https://github.com/juancarlosmiranda

Date: February 2021
Description:

Use:

"""
import os
import tkinter as tk
import webbrowser
from gui_benchmarking.gui_benchmarking_config import GUIBenchmarkingConfig


class HelpBenchmarkingWindow(tk.Toplevel):
    author_str = 'Juan Carlos Miranda'
    author_site_str = 'https://github.com/juancarlosmiranda'
    title_str = 'Azure Kinect Size Estimation & \n Weight Prediction Benchmarker \n(ak_sw_benchmarker)'
    version_number_str = '1.0'
    release_date = 'February 2022'

    def __init__(self, parent):
        super().__init__(parent)
        self.geometry(GUIBenchmarkingConfig.geometry_about)
        self.title('Help...')
        self.resizable(width=False, height=False)  # do not change the size
        self.attributes('-topmost', True)
        assets_path = os.path.dirname(os.path.abspath(__file__))
        img_path = os.path.join(assets_path, 'assets', 'icon_app.png')
        self.iconphoto(False, tk.PhotoImage(file=img_path))

        about_label = tk.Label(self, text=self.title_str + ' ' + self.version_number_str)
        about_label.config(font=("Verdana", 12))
        about_label.pack(anchor=tk.CENTER)
        text_info = tk.Label(self)
        help_text_info = f'Help window\n' \
                         f'Software under development \n' \
                         f'{self.version_number_str}\n'

        text_info['text'] = help_text_info
        text_info.pack(anchor=tk.CENTER)

        img_label = tk.Label(self)

        link = tk.Label(self, text="User manual here", font=('Helveticabold', 15), fg="blue", cursor="hand2")
        link.pack()
        link.bind("<Button-1>", lambda e:
        self.callback("https://github.com/GRAP-UdL-AT/ak_sw_benchmarker//"))

        buttonClose = tk.Button(self, text='Close', command=self.destroy)
        buttonClose.pack(expand=True)

    def callback(self, url):
        webbrowser.open_new_tab(url)
