import hashlib
import os
import platform
import subprocess
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.textinput import TextInput

# مفتاح سري لتوليد وترخيص المفاتيح بأمان
SECRET_SALT = 'TikFPS_Secret_Key_2026_Secure'


def get_device_request_code():
  """توليد كود فريد خاص بالجهاز بناءً على خصائصه"""
  try:
    if platform.system() == 'Android':
      from jnius import autoclass

      VERSION = autoclass('android.os.Build$VERSION')
      board = autoclass('android.os.Build').BOARD
      brand = autoclass('android.os.Build').BRAND
      device_id = f'{brand}-{board}-{VERSION.SDK_INT}'
    else:
      device_id = (
          platform.node()
          + platform.processor()
          + platform.machine()
          + str(os.getuid() if hasattr(os, 'getuid') else 1000)
      )
  except Exception:
    device_id = 'TikFPS_Default_Device_2026'

  hash_object = hashlib.sha256((device_id + SECRET_SALT).encode('utf-8'))
  full_hash = hash_object.hexdigest().upper()
  return f'{full_hash[:4]}-{full_hash[4:8]}'


def verify_activation_key(request_code, entered_key):
  """التحقق من صحة المفتاح المدخل مقارنة بكود الجهاز"""
  clean_key = entered_key.strip().upper()
  expected_hash = hashlib.sha256(
      (request_code + SECRET_SALT).encode('utf-8')
  ).hexdigest()
  expected_key = f'{expected_hash[:4]}-{expected_hash[4:8]}'.upper()
  return clean_key == expected_key


class ActivationScreen(Screen):

  def __init__(self, **kwargs):
    super().__init__(**kwargs)

    root_layout = FloatLayout()

    # جلب مسار الخلفية المطلق
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

    # عنوان التطبيق
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

    # كود الجهاز
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

    # معلومات الدفع
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

    # حقل إدخال المفتاح
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

    # زر التفعيل
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

    # رسالة الحالة
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

      # حفظ ملف الترخيص محلياً لكي لا يطلب التفعيل مرة أخرى
      current_dir = os.path.dirname(os.path.abspath(__file__))
      with open(os.path.join(current_dir, 'license.key'), 'w') as f:
        f.write(entered_key)

      # الانتقال لشاشة التطبيق الرئيسية بعد ثانية
      App.get_running_app().root.current = 'main_app'
    else:
      self.status_label.text = 'Invalid Key, Please Try Again!'
      self.status_label.color = (1, 0.3, 0.3, 1)


class MainAppScreen(Screen):
  """شاشة التطبيق الرئيسية التي تظهر بعد التفعيل الناجح"""

  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    layout = BoxLayout(orientation='vertical', padding=30, spacing=20)
    layout.add_widget(
        Label(
            text='Welcome to TikFPS Studio!\nApp is Fully Activated.',
            font_size='20sp',
            halign='center',
            markup=True,
        )
    )

    btn_back = Button(
        text='Settings / Exit',
        size_hint_y=None,
        height=50,
        background_color=(0.2, 0.2, 0.2, 1),
    )
    layout.add_widget(btn_back)
    self.add_widget(layout)


class TikFPSApp(App):

  def build(self):
    sm = ScreenManager()

    current_dir = os.path.dirname(os.path.abspath(__file__))
    license_path = os.path.join(current_dir, 'license.key')

    is_activated = False
    if os.path.exists(license_path):
      with open(license_path, 'r') as f:
        saved_key = f.read().strip()
        dummy_screen = ActivationScreen()
        if verify_activation_key(dummy_screen.device_code, saved_key):
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
