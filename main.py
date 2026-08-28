import os
import threading
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
            text="TikFPS: Select Video",
            font_size='18sp',
            halign='center',
            valign='middle'
        )
        layout.add_widget(self.label)

        btn_select = Button(
            text="1. Select Video from Gallery",
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
                # طلب أذونات التخزين الآمنة المتوافقة مع جميع إصدارات أندرويد في Kivy
                request_permissions([
                    Permission.READ_EXTERNAL_STORAGE,
                    Permission.WRITE_EXTERNAL_STORAGE
                ], self.on_permission_result)
            except Exception as e:
                self.open_gallery()
        else:
            self.open_gallery()

    def on_permission_result(self, permissions, grant_results):
        # فتح المعرض بغض النظر عن النتيجة (سيفتح لو الأذن متاح)
        Clock.schedule_once(lambda dt: self.open_gallery(), 0.2)

    def open_gallery(self, *args):
        try:
            filechooser.open_file(on_selection=self.on_video_selected)
        except Exception as e:
            self.label.text = f"Error opening filechooser: {str(e)}"

    def on_video_selected(self, selection):
        if selection and len(selection) > 0:
            self.selected_video = selection[0]
            Clock.schedule_once(self.update_ui)

    def update_ui(self, dt):
        filename = os.path.basename(self.selected_video)
        self.label.text = f"Selected Video:\n{filename}"

    def process_video(self, instance):
        if not self.selected_video:
            self.label.text = "Please select a video first!"
            return
        
        self.label.text = "Processing Video... Please wait"
        threading.Thread(target=self.run_ffmpeg_command).start()

    def run_ffmpeg_command(self):
        import subprocess

        dir_name = os.path.dirname(self.selected_video)
        base_name = os.path.basename(self.selected_video)
        name, ext = os.path.splitext(base_name)
        
        output_dir = "/sdcard/Download" if platform == 'android' else dir_name
        if not os.path.exists(output_dir):
            output_dir = dir_name

        output_path = os.path.join(output_dir, f"{name}_double{ext}")

        ffmpeg_bin = "ffmpeg"
        if platform == 'android':
            possible_path = os.path.join(os.environ.get('PYTHONHOME', ''), 'lib', 'libffmpeg.so')
            if os.path.exists(possible_path):
                ffmpeg_bin = possible_path

        cmd = [
            ffmpeg_bin,
            "-y",
            "-i", self.selected_video,
            "-c", "copy",
            "-bsf:v", "setts=ts=TS*2",
            "-bsf:a", "setts=ts=TS*2",
            "-video_track_timescale", "90000",
            "-brand", "isom",
            output_path
        ]

        try:
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode == 0:
                msg = f"Done!\nSaved to Downloads as:\n{name}_double{ext}"
            else:
                msg = f"Failed!\n{result.stderr[-200:]}"
        except Exception as e:
            msg = f"Error: {str(e)}"

        Clock.schedule_once(lambda dt: self.set_status(msg))

    def set_status(self, text):
        self.label.text = text

if __name__ == '__main__':
    TikFPSApp().run()
