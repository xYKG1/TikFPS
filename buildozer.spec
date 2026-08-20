[app]

# (str) Title of your application
title = TikFPS

# (str) Package name
package.name = tikfps

# (str) Package domain (needed for android/ios packaging)
package.domain = com.tikfps

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include
source.include_exts = py,png,jpg,kv,atlas

# (str) Application versioning
version = 0.1

# (list) Application requirements
requirements = python3,kivy,plyer,pyjnius

# (str) Supported orientation
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (list) Permissions
android.permissions = READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, READ_MEDIA_VIDEO

# (int) Target Android API
android.api = 33

# (int) Minimum API required
android.minapi = 24

# (str) Android NDK version
android.ndk = 25b

# (list) The Android archs to build for
android.archs = arm64-v8a

# (bool) Accept SDK licenses automatically
android.accept_sdk_license = True

# (list) Gradle dependencies
android.gradle_dependencies = com.arthenica:ffmpeg-kit-full:4.4

[buildozer]

# (int) Log level
log_level = 1

# (int) Display warning if buildozer is run as root
warn_on_root = 0
