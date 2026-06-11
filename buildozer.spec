[app]
title = Snake Game
package.name = snakegame
package.domain = org.soyan

source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,json,atlas

version = 1.0

requirements = python3,kivy

orientation = portrait
fullscreen = 1

android.api = 34
android.minapi = 21
android.archs = arm64-v8a, armeabi-v7a

[buildozer]
log_level = 2
warn_on_root = 1
