[app]
title = TikFPS
package.name = tikfps
package.domain = com.tikfps
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1
requirements = python3,kivy,plyer,pyjnius
p4a.branch = v2024.01.21
orientation = portrait
fullscreen = 0
android.permissions = READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, READ_MEDIA_VIDEO
android.gradle_dependencies = com.arthenica:ffmpeg-kit-full:4.5.LTS
android.add_gradle_repositories = mavenCentral(), google()
android.enable_androidx = True
android.api = 31
android.minapi = 24
android.ndk = 25b
android.archs = arm64-v8a
android.accept_sdk_license = True
[buildozer]
log_level = 2
warn_on_root = 0
