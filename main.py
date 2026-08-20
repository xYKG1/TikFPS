import os
import subprocess
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from plyer import filechooser

class TikFPSApp(App):
    def build(self):
        self.title = "TikFPS"
        self.selected_file = None
        layout = BoxLayout(orientation='vertical', padding=30, spacing=20)
        self.lbl = Label(text="TikFPS: Select Video", font_size='18sp')
        btn_pick = Button(text="1. Select Video from Gallery", size_hint=(1, 0.3), background_color=(0.2, 0.6, 1, 1))
        btn_pick.bind(on_press=self.pick_video)
        btn_run = Button(text="2. Process Video", size_hint=(1, 0.3), background_color=(0.2, 0.8, 0.2, 1))
        btn_run.bind(on_press=self.process_video)
        layout.add_widget(self.lbl)
        layout.add_widget(btn_pick)
        layout.add_widget(btn_run)
        return layout

    def pick_video(self, instance):
        filechooser.open_file(on_selection=self.on_select)

    def on_select(self, selection):
        if selection:
            self.selected_file = selection[0]
            self.lbl.text = f"Selected: {os.path.basename(self.selected_file)}"

    def process_video(self, instance):
        if not self.selected_file:
            self.lbl.text = "Please select a video first!"
            return
        out_file = os.path.splitext(self.selected_file)[0] + "_TikFPS.mp4"
        cmd = f'ffmpeg -y -i "{self.selected_file}" -c copy -bsf:v setts=ts=TS*2 -bsf:a setts=ts=TS*2 -video_track_timescale 90000 -brand isom "{out_file}"'
        try:
            self.lbl.text = "Processing..."
            subprocess.run(cmd, shell=True, check=True)
            self.lbl.text = f"Done! Saved: {os.path.basename(out_file)}"
        except Exception as e:
            self.lbl.text = "Error during processing"

if __name__ == '__main__':
    TikFPSApp().run()
