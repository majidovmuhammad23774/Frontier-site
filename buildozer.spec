[app]
title = БРОНЕЛОМ
package.name = bronelom
package.domain = io.github.majidovmuhammad23774

source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,ttf,mp3,ogg,wav,json,txt,zip
source.include_patterns = game/*,game/images/*,game/sound/*,game/avatar_game/*,main.py,version.json
source.exclude_dirs = tests,bin,.buildozer,.github,__pycache__,.git

version = 12.3.1

requirements = python3==3.10.13,kivy==2.2.1,pyjnius,android,pillow

orientation = portrait
fullscreen = 0
window_softinput_mode = below_target

# ⚠️ Фиксы для p4a + Python 3.13+
p4a.branch = develop
p4a.hostpython = /usr/bin/python3.10
p4a.bootstrap = sdl2

android.api = 33
android.minapi = 24
android.ndk = 25b
android.ndk_api = 24
android.archs = arm64-v8a
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

android.allow_backup = True
android.accept_sdk_license = True

# Иконка (если есть в game/avatar_game/avatar.png — раскомментируй)
# icon.filename = %(source.dir)s/game/avatar_game/avatar.png

[buildozer]
log_level = 2
warn_on_root = 0