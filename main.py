import os
import subprocess
import threading
import hashlib
import random
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.clock import Clock
from plyer import filechooser
from kivy.utils import platform

# ==========================================
# 0. دوال الحماية والتفعيل الداخلية
# ==========================================
SECRET_SALT = 'TikFPS_Secret_Key_2026_Secure'

def get_data_dir():
    app = App.get_running_app()
    if app and app.user_data_dir:
        return app.user_data_dir
    return os.path.dirname(os.path.abspath(__file__))

def get_device_request_code():
    data_dir = get_data_dir()
    code_path = os.path.join(data_dir, 'device.id')
    if os.path.exists(code_path):
        try:
            with open(code_path, 'r') as f:
                code = f.read().strip()
                if code: return code
        except Exception:
            pass
    code = f"{random.randint(1000, 9999)}-{random.randint(1000, 9999)}"
    try:
        with open(code_path, 'w') as f:
            f.write(code)
    except Exception:
        pass
    return code

def verify_key_logic(device_code, user_key):
    raw_data = device_code.strip() + SECRET_SALT
    full_hash = hashlib.sha256(raw_data.encode()).hexdigest().upper()
    expected_key = f"{full_hash[:4]}-{full_hash[4:8]}-{full_hash[8:12]}"
    return user_key.strip().upper() == expected_key

def is_activated():
    data_dir = get_data_dir()
    license_path = os.path.join(data_dir, 'license.key')
    if not os.path.exists(license_path):
        return False
    try:
        with open(license_path, 'r') as f:
            saved_key = f.read().strip()
        return verify_key_logic(get_device_request_code(), saved_key)
    except Exception:
        return False

def verify_and_activate(user_key):
    current_device_code = get_device_request_code()
    if verify_key_logic(current_device_code, user_key):
        try:
            data_dir = get_data_dir()
            license_path = os.path.join(data_dir, 'license.key')
            with open(license_path, 'w') as f:
                f.write(user_key.strip().upper())
            return True
        except Exception:
            return False
    return False

# ==========================================
# 1. شاشة التفعيل وحماية التطبيق
# ==========================================
class ActivationScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        anchor = AnchorLayout(anchor_x='center', anchor_y='center')
        layout = BoxLayout(orientation='vertical', padding=25, spacing=15, size_hint=(0.95, None), height=430)
        
        layout.add_widget(Label(text="TikFPS - Activation", font_size='22sp', bold=True, size_hint_y=None, height=40, halign='center'))
        
        self.device_code = get_device_request_code()
        layout.add_widget(Label(text=f"Your Device Code:\n[b]{self.device_code}[/b]", markup=True, font_size='18sp', halign='center', size_hint_y=None, height=65))
        
        layout.add_widget(Label(text="--- Payment via Zain Cash ---\nSend Request Code to Telegram Admin\nto get your Activation Key.", font_size='13sp', halign='center', size_hint_y=None, height=75))
        
        self.key_input = TextInput(hint_text="Enter Activation Key Here", multiline=False, size_hint_y=None, height=45, halign='center')
        layout.add_widget(self.key_input)
        
        btn_activate = Button(text="Activate App", size_hint_y=None, height=45, background_color=(0.1, 0.5, 0.1, 1))
        btn_activate.bind(on_press=self.verify_key)
        layout.add_widget(btn_activate)
        
        self.status_label = Label(text="", color=(1, 0.3, 0.3, 1), size_hint_y=None, height=30, halign='center')
        layout.add_widget(self.status_label)
        
        anchor.add_widget(layout)
        self.add_widget(anchor)

    def verify_key(self, instance):
        user_key = self.key_input.text
        if verify_and_activate(user_key):
            self.status_label.text = "Activated Successfully!"
            self.status_label.color = (0.3, 1, 0.3, 1)
            Clock.schedule_once(lambda dt: setattr(App.get_running_app().root, 'current', 'video_screen'), 1)
        else:
            self.status_label.text = "Invalid Key! Check and try again."

# ==========================================
# 2. واجهة التطبيق الأصلية لتعديل الفيديوهات
# ==========================================
class VideoProcessorScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_video = None
        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        
        self.label = Label(
            text="TikFPS\nSelect a video to process",
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

        self.add_widget(layout)

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
            self.label.text = f"Gallery Error: {str(e)}"

    def on_video_selected(self, selection):
        if selection and len(selection) > 0:
            self.selected_video = selection[0]
            Clock.schedule_once(self.update_ui)

    def update_ui(self, dt):
        filename = os.path.basename(self.selected_video)
        self.label.text = f"Selected File:\n{filename}"

    def process_video(self, instance):
        if not self.selected_video:
            self.label.text = "Please select a video first!"
            return
        
        self.label.text = "Processing video...\nPlease wait"
        threading.Thread(target=self.run_ffmpeg).start()

    def run_ffmpeg(self):
        try:
            if platform == 'android':
                from android.storage import primary_external_storage_path
                storage_dir = os.path.join(primary_external_storage_path(), 'Download')
            else:
                storage_dir = os.path.dirname(self.selected_video)

            os.makedirs(storage_dir, exist_ok=True)
            output_file = os.path.join(storage_dir, f"patched_{os.path.basename(self.selected_video)}")

            cmd = [
                "ffmpeg", "-y",
                "-i", self.selected_video,
                "-c", "copy",
                "-bsf:v", "setts=ts=TS*2",
                "-bsf:a", "setts=ts=TS*2",
                "-video_track_timescale", "90000",
                "-brand", "isom",
                output_file
            ]

            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()

            if process.returncode == 0:
                if platform == 'android':
                    self.scan_file_to_gallery(output_file)
                self.set_status(f"Success!\nSaved in Downloads:\n{os.path.basename(output_file)}")
            else:
                self.set_status(f"FFmpeg Error:\n{stderr.decode('utf-8')[:150]}")

        except Exception as e:
            self.set_status(f"Error:\n{str(e)}")

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

# ==========================================
# 3. تشغيل التطبيق وإدارة الشاشات
# ==========================================
class TikFPSApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(ActivationScreen(name='activation_screen'))
        sm.add_widget(VideoProcessorScreen(name='video_screen'))
        
        if is_activated():
            sm.current = 'video_screen'
        else:
            sm.current = 'activation_screen'
            
        return sm

if __name__ == '__main__':
    TikFPSApp().run()
