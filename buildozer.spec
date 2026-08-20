[app]
title = TikFPS
package.name = tikfps
package.domain = com.tikfps
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1
requirements = python3,kivy,plyer,pyjnius
orientation = portrait
fullscreen = 0
android.permissions = READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, READ_MEDIA_VIDEO
android.api = 33
android.minapi = 24
# إجبار النظام على استخدام هذا الإصدار
android.ndk = 25b
android.archs = arm64-v8a
android.accept_sdk_license = True
android.gradle_dependencies = com.arthenica:ffmpeg-kit-full:4.5.LTS

[buildozer]
log_level = 2
warn_on_root = 0
