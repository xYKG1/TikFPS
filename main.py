import os
import sys
import threading
import subprocess
import traceback

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
from plyer import filechooser
from kivy.utils import platform

class TikFPSApp(App):
    def build(self):
        self.selected_video = None
        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        
        self.label = Label(
            text="TikFPS: Ready",
            font_size='16sp',
            halign='center',
            valign='middle'
        )
        layout.add_widget(self.label)

        btn_select = Button(
            text="1. Select Video",
            background_color=(0.1, 0.3, 0.5, 1),
            size_hint_y=0.25
        )
        btn_select.bind(on_release=self.request_and_open)
        layout.add_widget(btn_select)

        btn_process = Button(
            text="2. Process Video",
            background_color=(0.1, 0.4, 0.1, 1),
            size_hint_y=0.25
        )
        btn_process.bind(on_release=self.process_video)
        layout.add_widget(btn_process)

        return layout

    def request_and_open(self, instance):
        if platform == 'android':
            try:
                from android.permissions import request_permissions, Permission
                request_permissions([
                    Permission.READ_EXTERNAL_STORAGE,
                    Permission.WRITE_EXTERNAL_STORAGE
                ], self.on_permission_result)
            except Exception as e:
                self.label.text = f"Perm Error: {str(e)}"
                self.open_gallery()
        else:
            self.open_gallery()

    def on_permission_result(self, permissions, grant_results):
        Clock.schedule_once(lambda dt: self.open_gallery(), 0.2)

    def open_gallery(self, *args):
        try:
            filechooser.open_file(on_selection=self.on_video_selected)
        except Exception as e:
            self.label.text = f"Gallery Error: {str(e)}"

    def on_video_selected(self, selection):
        if selection and len(selection) > 0:
            self.selected_video = selection[0]
            Clock.schedule_once(self.update_ui)

    def update_ui(self, dt):
        filename = os.path.basename(self.selected_video)
        self.label.text = f"Selected:\n{filename}"

    def process_video(self, instance):
        if not self.selected_video:
            self.label.text = "Please select a video first!"
            return
        
        self.label.text = "Processing Video...\nPlease wait."
        threading.Thread(target=self.run_ffmpeg_command).start()

    def run_ffmpeg_command(self):
        try:
            output_dir = os.path.dirname(self.selected_video)
            output_file = os.path.join(output_dir, "processed_tikfps.mp4")
            
            ffmpeg_bin = 'ffmpeg'
            
            # البحث عن مسار ffmpeg التنفيذي في أندرويد
            if platform == 'android':
                from jnius import autoclass
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                activity = PythonActivity.mActivity
                lib_dir = activity.getApplicationInfo().nativeLibraryDir
                possible_ffmpeg = os.path.join(lib_dir, 'libffmpeg.so')
                
                if os.path.exists(possible_ffmpeg):
                    ffmpeg_bin = possible_ffmpeg

            cmd = [
                ffmpeg_bin, '-y',
                '-i', self.selected_video,
                '-c:v', 'libx264',
                '-preset', 'ultrafast',
                output_file
            ]
            
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()

            if process.returncode == 0:
                self.set_status(f"Done!\nSaved to: {os.path.basename(output_file)}")
            else:
                self.set_status(f"FFmpeg Error:\n{stderr.decode('utf-8')[-200:]}")
        except Exception as e:
            self.set_status(f"Error: {str(e)}")

    def set_status(self, text):
        Clock.schedule_once(lambda dt: setattr(self.label, 'text', text))

if __name__ == '__main__':
    TikFPSApp().run()
