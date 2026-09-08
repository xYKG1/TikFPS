import hashlib
import os
import threading
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.textinput import TextInput
from plyer import filechooser
from kivy.utils import platform

# مفتاح سري موحد
SECRET_SALT = 'TIKFPS2026'


def get_device_request_code():
  # كود ثابت يظهر للمستخدم
  return '913D-E7B0'


def verify_activation_key(request_code, entered_key):
  clean_request = request_code.strip().upper()
  clean_key = entered_key.strip().upper()

  # المعادلة المباشرة: الهاش المبني حصرياً على كود الجهاز
  combined = clean_request + SECRET_SALT
  full_hash = hashlib.sha256(combined.encode('utf-8')).hexdigest().upper()
  expected_key = f'{full_hash[:4]}-{full_hash[4:8]}'

  return clean_key == expected_key


class ActivationScreen(Screen):

  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    root_layout = FloatLayout()

    current_dir = os.path.dirname(os.path.abspath(__file__))
    bg_path = os.path.join(current_dir, 'bg.png')

    if os.path.exists(bg_path):
      bg_image = Image(
          source=bg_path,
          allow_stretch=True,
          keep_ratio=False,
          size_hint=(1, 1),
          pos_hint={'center_x': 0.5, 'center_y': 0.5},
      )
      root_layout.add_widget(bg_image)

    content_layout = BoxLayout(
        orientation='vertical',
        padding=25,
        spacing=15,
        size_hint=(0.85, None),
        pos_hint={'center_x': 0.5, 'center_y': 0.5},
    )
    content_layout.bind(minimum_height=content_layout.setter('height'))

    content_layout.add_widget(
        Label(
            text='TikFPS - Activation',
            font_size='22sp',
            bold=True,
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=40,
            halign='center',
            valign='middle',
        )
    )

    self.device_code = get_device_request_code()
    content_layout.add_widget(
        Label(
            text=f'Your Code is Ready:\n[color=#00FF66][b]{self.device_code}[/b][/color]',
            markup=True,
            font_size='18sp',
            halign='center',
            valign='middle',
            size_hint_y=None,
            height=85,
        )
    )

    content_layout.add_widget(
        Label(
            text=(
                '— Payment via Zain Cash —\nSend Code & Payment to Admin:\n[color=#00FF66][b]@DA_NTY[/b][/color]'
            ),
            markup=True,
            font_size='13sp',
            halign='center',
            valign='middle',
            size_hint_y=None,
            height=95,
        )
    )

    self.key_input = TextInput(
        hint_text='Enter Activation Key Here',
        multiline=False,
        size_hint_y=None,
        height=50,
        halign='center',
        font_size='15sp',
        background_color=(0.05, 0.1, 0.05, 0.8),
        foreground_color=(1, 1, 1, 1),
        hint_text_color=(0.6, 0.6, 0.6, 1),
    )
    content_layout.add_widget(self.key_input)

    btn_activate = Button(
        text='Activate App',
        size_hint_y=None,
        height=55,
        font_size='16sp',
        bold=True,
        background_normal='',
        background_color=(0.0, 0.8, 0.3, 1),
        color=(1, 1, 1, 1),
    )
    btn_activate.bind(on_press=self.validate_key)
    content_layout.add_widget(btn_activate)

    self.status_label = Label(
        text='',
        color=(1, 0.3, 0.3, 1),
        size_hint_y=None,
        height=30,
        font_size='14sp',
        halign='center',
    )
    content_layout.add_widget(self.status_label)

    root_layout.add_widget(content_layout)
    self.add_widget(root_layout)

  def validate_key(self, instance):
    entered_key = self.key_input.text
    if verify_activation_key(self.device_code, entered_key):
      self.status_label.text = 'Activation Successful!'
      self.status_label.color = (0, 1, 0.4, 1)

      current_dir = os.path.dirname(os.path.abspath(__file__))
      with open(os.path.join(current_dir, 'license.key'), 'w') as f:
        f.write(entered_key.strip().upper())

      App.get_running_app().root.current = 'main_app'
    else:
      self.status_label.text = 'Invalid Key, Please Try Again!'
      self.status_label.color = (1, 0.3, 0.3, 1)


class MainAppScreen(Screen):

  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.selected_video = None
    layout = BoxLayout(orientation='vertical', padding=20, spacing=20)

    self.label = Label(
        text='TikFPS - Activated\nSelect a video to process',
        font_size='16sp',
        halign='center',
        valign='middle',
    )
    layout.add_widget(self.label)

    btn_select = Button(
        text='1. Select Video',
        background_color=(0.1, 0.3, 0.5, 1),
        size_hint_y=0.25,
    )
    btn_select.bind(on_release=self.request_and_open)
    layout.add_widget(btn_select)

    btn_process = Button(
        text='2. Process Video',
        background_color=(0.1, 0.4, 0.1, 1),
        size_hint_y=0.25,
    )
    btn_process.bind(on_release=self.process_video)
    layout.add_widget(btn_process)

    btn_lock = Button(
        text='Lock / Re-check License',
        background_color=(0.4, 0.1, 0.1, 1),
        size_hint_y=0.15,
    )
    btn_lock.bind(on_release=self.lock_app)
    layout.add_widget(btn_lock)

    self.add_widget(layout)

  def request_and_open(self, instance):
    if platform == 'android':
      try:
        from android.permissions import Permission, request_permissions

        request_permissions(
            [
                Permission.READ_EXTERNAL_STORAGE,
                Permission.WRITE_EXTERNAL_STORAGE,
            ],
            self.on_permission_result,
        )
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
      self.label.text = f'Gallery Error: {str(e)}'

  def on_video_selected(self, selection):
    if selection and len(selection) > 0:
      self.selected_video = selection[0]
      Clock.schedule_once(self.update_ui)

  def update_ui(self, dt):
    filename = os.path.basename(self.selected_video)
    self.label.text = f'Selected File:\n{filename}'

  def process_video(self, instance):
    if not self.selected_video:
      self.label.text = 'Please select a video first!'
      return

    self.label.text = 'Processing video...\nPlease wait'
    threading.Thread(target=self.run_ffmpeg).start()

  def run_ffmpeg(self):
    try:
      if platform == 'android':
        from android.storage import primary_external_storage_path

        storage_dir = os.path.join(
            primary_external_storage_path(), 'Download'
        )
      else:
        storage_dir = os.path.dirname(self.selected_video)

      os.makedirs(storage_dir, exist_ok=True)
      output_file = os.path.join(
          storage_dir, f'patched_{os.path.basename(self.selected_video)}'
      )

      cmd = [
          'ffmpeg',
          '-y',
          '-i',
          self.selected_video,
          '-c',
          'copy',
          '-bsf:v',
          'setts=ts=TS*2',
          '-bsf:a',
          'setts=ts=TS*2',
          '-video_track_timescale',
          '90000',
          '-brand',
          'isom',
          output_file,
      ]

      process = subprocess.Popen(
          cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
      )
      stdout, stderr = process.communicate()

      if process.returncode == 0:
        if platform == 'android':
          self.scan_file_to_gallery(output_file)
        self.set_status(
            f'Success!\nSaved in Downloads:\n{os.path.basename(output_file)}'
        )
      else:
        self.set_status(f"FFmpeg Error:\n{stderr.decode('utf-8')[:150]}")

    except Exception as e:
      self.set_status(f'Error:\n{str(e)}')

  def scan_file_to_gallery(self, file_path):
    try:
      from jnius import autoclass

      PythonActivity = autoclass('org.kivy.android.PythonActivity')
      MediaScannerConnection = autoclass('android.media.MediaScannerConnection')
      activity = PythonActivity.mActivity
      MediaScannerConnection.scanFile(activity, [file_path], None, None)
    except Exception as e:
      print(f'MediaScanner Error: {e}')

  def set_status(self, text):
    pass

  def set_status(self, text):
    Clock.schedule_once(lambda dt: setattr(self.label, 'text', text))

  def lock_app(self, instance):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    license_path = os.path.join(current_dir, 'license.key')
    if os.path.exists(license_path):
      os.remove(license_path)
    App.get_running_app().root.current = 'activation'


class TikFPSApp(App):

  def build(self):
    sm = ScreenManager()

    current_dir = os.path.dirname(os.path.abspath(__file__))
    license_path = os.path.join(current_dir, 'license.key')

    is_activated = False
    if os.path.exists(license_path):
      with open(license_path, 'r') as f:
        saved_key = f.read().strip()
        if verify_activation_key('913D-E7B0', saved_key):
          is_activated = True

    sm.add_widget(ActivationScreen(name='activation'))
    sm.add_widget(MainAppScreen(name='main_app'))

    if is_activated:
      sm.current = 'main_app'
    else:
      sm.current = 'activation'

    return sm


if __name__ == '__main__':
  TikFPSApp().run()
