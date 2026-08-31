import os
import sys
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
        threading.Thread(target=self.run_native_ffmpeg).start()

    def run_native_ffmpeg(self):
        try:
            if platform == 'android':
                from android.storage import primary_external_storage_path
                storage_dir = os.path.join(primary_external_storage_path(), 'Download')
            else:
                storage_dir = os.path.dirname(self.selected_video)

            os.makedirs(storage_dir, exist_ok=True)
            output_file = os.path.join(storage_dir, f"patched_{os.path.basename(self.selected_video)}")

            # أمر FFmpeg المطلوب كـ string
            cmd_str = f"-y -i \"{self.selected_video}\" -c copy -bsf:v setts=ts=TS*2 -bsf:a setts=ts=TS*2 -video_track_timescale 90000 -brand isom \"{output_file}\""

            if platform == 'android':
                from jnius import autoclass
                FFmpegKit = autoclass('com.ffmpegkit.FFmpegKit')
                ReturnCode = autoclass('com.ffmpegkit.ReturnCode')
                
                session = FFmpegKit.execute(cmd_str)
                if ReturnCode.isSuccess(session.getReturnCode()):
                    self.scan_file_to_gallery(output_file)
                    self.set_status(f"Success!\nSaved to Downloads:\n{os.path.basename(output_file)}")
                else:
                    self.set_status(f"FFmpeg Execution Failed!\nCode: {session.getReturnCode()}")
            else:
                self.set_status("Desktop simulation completed.")

        except Exception as e:
            self.set_status(f"Error: {str(e)}")

    def scan_file_to_gallery(self, file_path):
        try:
            from jnius import autoclass
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            MediaScannerConnection = autoclass('android.media.MediaScannerConnection')
            
            activity = PythonActivity.mActivity
            MediaScannerConnection.scanFile(activity, [file_path], None, None)
        except Exception as e:
            print(f"MediaScanner Error: {e}")

    def set_status(self, text):
        Clock.schedule_once(lambda dt: setattr(self.label, 'text', text))

if __name__ == '__main__':
    TikFPSApp().run()
