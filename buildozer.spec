[app]
title = TikFPS
package.name = tikfps
package.domain = com.tikfps
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1
requirements = python3,kivy==2.2.1,plyer
orientation = portrait
fullscreen = 0
android.permissions = READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE
android.api = 31
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a
p4a.branch = master

[buildozer]
log_level = 2
warn_on_root = 0
