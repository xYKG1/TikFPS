[app]
title = TikFPS
package.name = tikfps
package.domain = com.tikfps
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1

requirements = python3==3.11.0,hostpython3==3.11.0,kivy==2.3.0,plyer,android

orientation = portrait
fullscreen = 0
android.permissions = READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, READ_MEDIA_IMAGES, READ_MEDIA_VIDEO
android.api = 31
android.minapi = 24
android.ndk = 25b
android.archs = arm64-v8a
android.accept_sdk_license = True
android.gradle_dependencies = com.ffmpegkit:ffmpeg-kit-full:5.1

[buildozer]
log_level = 2
warn_on_root = 0
