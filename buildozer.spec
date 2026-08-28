[app]
title = TikFPS
package.name = tikfps
package.domain = com.tikfps
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1

# تثبيت إصدار Kivy المستقر وتجنب تعارضات Cython
requirements = python3,kivy==2.2.1,plyer,pyjnius,cython==0.29.33
p4a.branch = master
orientation = portrait
fullscreen = 0
android.permissions = READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, READ_MEDIA_VIDEO
android.api = 31
android.minapi = 24
android.ndk = 25b
android.archs = arm64-v8a
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 0
