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
            from android.permissions import request_permissions, Permission
            request_permissions(
                [Permission.READ_MEDIA_VIDEO, Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE],
                self.open_gallery
            )
        else:
            self.open_gallery(None, None)

    def open_gallery(self, permissions, grants):
        filechooser.open_file(on_selection=self.on_video_selected)

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
        dir_name = os.path.dirname(self.selected_video)
        base_name = os.path.basename(self.selected_video)
        name, ext = os.path.splitext(base_name)
        
        output_path = os.path.join(dir_name, f"{name}_double{ext}")

        # نفس أمر FFmpeg الخاص بك لرباعية الإطارات / التوقيت
        cmd = f'-y -i "{self.selected_video}" -c copy -bsf:v setts=ts=TS*2 -bsf:a setts=ts=TS*2 -video_track_timescale 90000 -brand isom "{output_path}"'

        if platform == 'android':
            try:
                from jnius import autoclass
                FFmpegKit = autoclass('com.arthenica.ffmpegkit.FFmpegKit')
                ReturnCode = autoclass('com.arthenica.ffmpegkit.ReturnCode')

                session = FFmpegKit.execute(cmd)
                return_code = session.getReturnCode()

                if ReturnCode.isSuccess(return_code):
                    msg = f"Done!\nSaved as:\n{name}_double{ext}"
                else:
                    msg = "Failed to process video!"
            except Exception as e:
                msg = f"Error: {str(e)}"
        else:
            import subprocess
            try:
                subprocess.run(f"ffmpeg {cmd}", shell=True, check=True)
                msg = f"Done!\nSaved as:\n{name}_double{ext}"
            except Exception as e:
                msg = f"Error: {str(e)}"

        Clock.schedule_once(lambda dt: self.set_status(msg))

    def set_status(self, text):
        self.label.text = text

if __name__ == '__main__':
    TikFPSApp().run()
