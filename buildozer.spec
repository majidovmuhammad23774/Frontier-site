[app]
title = Bronelom
package.name = bronelom
package.domain = org.bronelom
source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,ttf,wav,mp3,ogg
version = 12.3.1
requirements = python3,kivy==2.2.1,pyjnius,android
orientation = portrait
fullscreen = 0
android.api = 33
android.minapi = 24
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.accept_sdk_license = True
android.private_storage = True

[buildozer]
log_level = 2
warn_on_root = 1

[p4a]
python_version = 3.11
