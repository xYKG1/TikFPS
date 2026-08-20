import os
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
            font_size='20sp',
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
        self.label.text = f"Processing: {os.path.basename(self.selected_video)}"

if __name__ == '__main__':
    TikFPSApp().run()
