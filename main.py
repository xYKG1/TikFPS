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
            text="TikFPS\nاختر فيديو للبدء",
            font_size='16sp',
            halign='center',
            valign='middle'
        )
        layout.add_widget(self.label)

        btn_select = Button(
            text="1. اختيار الفيديو",
            background_color=(0.1, 0.3, 0.5, 1),
            size_hint_y=0.25
        )
        btn_select.bind(on_release=self.request_and_open)
        layout.add_widget(btn_select)

        btn_process = Button(
            text="2. معالجة وحفظ",
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
                self.open_gallery()
        else:
            self.open_gallery()

    def on_permission_result(self, permissions, grant_results):
        Clock.schedule_once(lambda dt: self.open_gallery(), 0.2)

    def open_gallery(self, *args):
        try:
            filechooser.open_file(on_selection=self.on_video_selected)
        except Exception as e:
            self.label.text = f"خطأ في فتح المعرض: {str(e)}"

    def on_video_selected(self, selection):
        if selection and len(selection) > 0:
            self.selected_video = selection[0]
            Clock.schedule_once(self.update_ui)

    def update_ui(self, dt):
        filename = os.path.basename(self.selected_video)
        self.label.text = f"تم تحديد:\n{filename}"

    def process_video(self, instance):
        if not self.selected_video:
            self.label.text = "الرجاء اختيار فيديو أولاً!"
            return
        
        self.label.text = "جاري معالجة الفيديو...\nيرجى الانتظار"
        threading.Thread(target=self.run_ffmpeg_processing).start()

    def run_ffmpeg_processing(self):
        try:
            if platform == 'android':
                from android.storage import primary_external_storage_path
                storage_dir = os.path.join(primary_external_storage_path(), 'Download')
            else:
                storage_dir = os.path.dirname(self.selected_video)

            os.makedirs(storage_dir, exist_ok=True)
            output_file = os.path.join(storage_dir, f"tikfps_{os.path.basename(self.selected_video)}")

            # استدعاء ffmpeg-python للقيام بنفس عملية Bitstream Filters و Timescale
            import ffmpeg
            
            (
                ffmpeg
                .input(self.selected_video)
                .output(
                    output_file,
                    c='copy',
                    bsf_v='setts=ts=TS*2',
                    bsf_a='setts=ts=TS*2',
                    video_track_timescale=90000,
                    brand='isom'
                )
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True)
            )

            if platform == 'android':
                self.scan_file_to_gallery(output_file)

            self.set_status(f"تمت المعالجة بنجاح!\nتم الحفظ في التنزيلات:\n{os.path.basename(output_file)}")

        except Exception as e:
            self.set_status(f"خطأ أثناء المعالجة:\n{str(e)}")

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
