[app]
title = БРОНЕЛОМ
package.name = bronelom
package.domain = org.majidovmuhammad

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,mp3,wav

version = 12.3.1

requirements = python3,kivy,pillow

orientation = portrait
fullscreen = 0

android.permissions = INTERNET

android.api = 36
android.minapi = 21
android.ndk = 29

p4a.branch = develop

android.archs = arm64-v8a

android.allow_backup = True

[buildozer]
log_level = 2
warn_on_root = 1