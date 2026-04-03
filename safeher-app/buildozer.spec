[app]

# (str) Title of your application
title = SafeHer

# (str) Package name
package.name = safeher

# (str) Package domain (needed for android/ios packaging)
package.domain = com.safeher.app

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,ttf

# (list) List of inclusions using pattern matching
#source.include_patterns = assets/*,images/*.png

# (list) Source files to exclude
#source.exclude_exts = spec

# (str) Application versioning (method 1)
version = 1.0.0

# (str) Application versioning (method 2)
# version.regex = __version__ = ['"](.*)["]
# version.filename = %(source.dir)s/main.py

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3,kivy==2.3.0,kivymd==1.2.0,plyer==2.1.0,requests==2.31.0,pillow==10.1.0,numpy==1.24.3,geopy==2.4.1,bcrypt==4.1.1,python-jose[cryptography]==3.3.0

# (str) Presplash of the application
#presplash.filename = %(source.dir)s/assets/presplash.png

# (str) Icon of the application
icon.filename = %(source.dir)s/assets/icon.png

# (list) Supported orientations
# Valid options are: landscape, portrait, portrait-reverse or landscape-reverse
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

#
# Android specific
#

# (list) Permissions
android.permissions = INTERNET, ACCESS_FINE_LOCATION, ACCESS_COARSE_LOCATION, ACCESS_BACKGROUND_LOCATION, SEND_SMS, CALL_PHONE, READ_PHONE_STATE, VIBRATE, RECEIVE_BOOT_COMPLETED, FOREGROUND_SERVICE, CAMERA, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE

# (int) Target Android API, should be as high as possible.
android.api = 31

# (int) Minimum API your APK will support.
android.minapi = 21

# (str) Android NDK version to use
android.ndk = 23b

# (bool) If True, then skip trying to update the Android sdk
# This can be useful to avoid excess Internet downloads or save time
# when an update is due and you just want to test/build your package
android.skip_update = False

# (bool) If True, then automatically accept SDK license
# agreements. This is intended for automation only. If set to False,
# the default, you will be shown the license when first running
# buildozer.
android.accept_sdk_license = True

# (str) Android entry point, default is ok for kivy-based app
#android.entrypoint = org.renpy.android.PythonActivity

# (list) Android application meta-data to set (key=value format)
android.meta_data = 

# (list) Android library project to add (will be added in the
# project.properties automatically.)
android.library_references =

# (str) Android logcat filters to use
android.logcat_filters = *:S python:D

# (bool) Copy library instead of making a libpymodules.so
android.copy_libs = 1

# (list) The Android archs to build for, choices are armeabi-v7a, arm64-v8a, x86, x86_64
android.archs = armeabi-v7a, arm64-v8a

#
# Python for android (kivy)
#

# (str) Python branch to use, e.g. 3.8
python.branch = 3.11

# (str) Python commit, e.g. master
python.commit = master

# (bool) Force python implementation
python.implementation =cpython3

# (bool) Enable python3
python3 = True

# (str) Android entry point, default is ok for kivy-based app
#android.entrypoint = org.renpy.android.PythonActivity

# (str) Android app theme, default is ok for kivy-based app
#android.apptheme = "@android:style/Theme.NoTitleBar"

# (list) Pattern to whitelist for the whole project
#android.whitelist =

# (str) Path to a custom whitelist file
#android.whitelist_src =

# (str) Path to a custom blacklist file
#android.blacklist_src =

# (list) List of allowed Android libraries
#android.allowed_libraries =

# (int) Android minimum API
#android.minapi =

# (bool) If True, then copy instead of linking the python libraries
#android.copy_libs = 1

# (str) Android logcat filters to use
#android.logcat_filters =

# (bool) Enable AndroidX support
android.enable_androidx = True

# (str) The Android arch to build for, choices are armeabi-v7a, arm64-v8a, x86, x86_64
android.arch = armeabi-v7a

#
# iOS specific
#

# (str) Path to a custom kivy-ios directory
#ios.kivy_ios_dir = 

# (str) Name of the kivy-ios framework to use
#ios.kivy_ios_framework = 

# (bool) Force kivy-ios framework
#ios.kivy_ios_force_framework = False

# (bool) If True, then copy instead of linking the python libraries
#ios.copy_libs = 1

# (str) iOS deployment target
#ios.deployment_target = 12.0

# (list) iOS frameworks to add
#ios.frameworks = CoreLocation, CoreMotion, AVFoundation

# (bool) Enable storyboards support
#ios.storyboards = True

# (str) Identifier for the storyboards
#ios.storyboard_id = MainStoryboard

# (list) iOS entitlements to add
#ios.entitlements = 

# (str) Path to a custom plist file
#ios.plist_file = 

# (bool) If True, then add the kivy-ios framework to the project
#ios.kivy_ios_add_framework = True

# (str) iOS bundle identifier
#ios.bundle_identifier = com.safeher.app

# (str) iOS display name
#ios.display_name = SafeHer

# (str) iOS version
#ios.version = 1.0.0

# (bool) If True, then add the kivy-ios framework to the project
#ios.kivy_ios_add_framework = True

# (bool) If True, then copy instead of linking the python libraries
#ios.copy_libs = 1

# (str) Path to a custom kivy-ios directory
#ios.kivy_ios_dir = 

# (str) Name of the kivy-ios framework to use
#ios.kivy_ios_framework = 

# (bool) Force kivy-ios framework
#ios.kivy_ios_force_framework = False

# (str) iOS deployment target
#ios.deployment_target = 12.0

# (list) iOS frameworks to add
#ios.frameworks = CoreLocation, CoreMotion, AVFoundation

# (bool) Enable storyboards support
#ios.storyboards = True

# (str) Identifier for the storyboards
#ios.storyboard_id = MainStoryboard

# (list) iOS entitlements to add
#ios.entitlements = 

# (str) Path to a custom plist file
#ios.plist_file = 

# (bool) If True, then add the kivy-ios framework to the project
#ios.kivy_ios_add_framework = True

# (str) iOS bundle identifier
#ios.bundle_identifier = com.safeher.app

# (str) iOS display name
#ios.display_name = SafeHer

# (str) iOS version
#ios.version = 1.0.0

# (bool) If True, then copy instead of linking the python libraries
#ios.copy_libs = 1

#
# Mac specific
#

# (str) Path to a custom kivy-macos directory
#macos.kivy_macos_dir = 

# (str) Name of the kivy-macos framework to use
#macos.kivy_macos_framework = 

# (bool) Force kivy-macos framework
#macos.kivy_macos_force_framework = False

# (bool) If True, then copy instead of linking the python libraries
#macos.copy_libs = 1

# (str) Path to a custom kivy-macos directory
#macos.kivy_macos_dir = 

# (str) Name of the kivy-macos framework to use
#macos.kivy_macos_framework = 

# (bool) Force kivy-macos framework
#macos.kivy_macos_force_framework = False

# (bool) If True, then copy instead of linking the python libraries
#macos.copy_libs = 1

#
# Windows specific
#

# (str) Path to a custom kivy-win directory
#windows.kivy_win_dir = 

# (str) Name of the kivy-win framework to use
#windows.kivy_win_framework = 

# (bool) Force kivy-win framework
#windows.kivy_win_force_framework = False

# (bool) If True, then copy instead of linking the python libraries
#windows.copy_libs = 1

# (str) Path to a custom kivy-win directory
#windows.kivy_win_dir = 

# (str) Name of the kivy-win framework to use
#windows.kivy_win_framework = 

# (bool) Force kivy-win framework
#windows.kivy_win_force_framework = False

# (bool) If True, then copy instead of linking the python libraries
#windows.copy_libs = 1

#
# Linux specific
#

# (str) Path to a custom kivy-linux directory
#linux.kivy_linux_dir = 

# (str) Name of the kivy-linux framework to use
#linux.kivy_linux_framework = 

# (bool) Force kivy-linux framework
#linux.kivy_linux_force_framework = False

# (bool) If True, then copy instead of linking the python libraries
#linux.copy_libs = 1

# (str) Path to a custom kivy-linux directory
#linux.kivy_linux_dir = 

# (str) Name of the kivy-linux framework to use
#linux.kivy_linux_framework = 

# (bool) Force kivy-linux framework
#linux.kivy_linux_force_framework = False

# (bool) If True, then copy instead of linking the python libraries
#linux.copy_libs = 1

#
# Web specific
#

# (str) Path to a custom kivy-web directory
#web.kivy_web_dir = 

# (str) Name of the kivy-web framework to use
#web.kivy_web_framework = 

# (bool) Force kivy-web framework
#web.kivy_web_force_framework = False

# (bool) If True, then copy instead of linking the python libraries
#web.copy_libs = 1

# (str) Path to a custom kivy-web directory
#web.kivy_web_dir = 

# (str) Name of the kivy-web framework to use
#web.kivy_web_framework = 

# (bool) Force kivy-web framework
#web.kivy_web_force_framework = False

# (bool) If True, then copy instead of linking the python libraries
#web.copy_libs = 1

#
# Buildozer specific
#

# (str) The directory where buildozer will store the built packages
#buildozer.build_dir = ./build

# (str) The directory where buildozer will store the built packages
#buildozer.output_dir = ./bin

# (str) The directory where buildozer will store the built packages
#buildozer.cache_dir = ./.buildozer

# (str) The directory where buildozer will store the built packages
#buildozer.global_config_dir = ~/.buildozer

# (str) The directory where buildozer will store the built packages
#buildozer.local_config_dir = ./buildozer.spec

# (str) The directory where buildozer will store the built packages
#buildozer.spec = ./buildozer.spec

# (str) The directory where buildozer will store the built packages
#buildozer.specname = safeher

# (str) The directory where buildozer will store the built packages
#buildozer.version = 1.0.0

# (str) The directory where buildozer will store the built packages
#buildozer.filename = safeher

# (str) The directory where buildozer will store the built packages
#buildozer.icon = %(source.dir)s/assets/icon.png

# (str) The directory where buildozer will store the built packages
#buildozer.presplash = %(source.dir)s/assets/presplash.png

# (str) The directory where buildozer will store the built packages
#buildozer.orientation = portrait

# (str) The directory where buildozer will store the built packages
#buildozer.fullscreen = 0

# (str) The directory where buildozer will store the built packages
#buildozer.android.permissions = INTERNET, ACCESS_FINE_LOCATION, ACCESS_COARSE_LOCATION, ACCESS_BACKGROUND_LOCATION, SEND_SMS, CALL_PHONE, READ_PHONE_STATE, VIBRATE, RECEIVE_BOOT_COMPLETED, FOREGROUND_SERVICE, CAMERA, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE

# (str) The directory where buildozer will store the built packages
#buildozer.android.api = 31

# (str) The directory where buildozer will store the built packages
#buildozer.android.minapi = 21

# (str) The directory where buildozer will store the built packages
#buildozer.android.ndk = 23b

# (str) The directory where buildozer will store the built packages
#buildozer.android.skip_update = False

# (str) The directory where buildozer will store the built packages
#buildozer.android.accept_sdk_license = True

# (str) The directory where buildozer will store the built packages
#buildozer.android.meta_data = 

# (str) The directory where buildozer will store the built packages
#buildozer.android.library_references =

# (str) The directory where buildozer will store the built packages
#buildozer.android.logcat_filters = *:S python:D

# (str) The directory where buildozer will store the built packages
#buildozer.android.copy_libs = 1

# (str) The directory where buildozer will store the built packages
#buildozer.android.archs = armeabi-v7a, arm64-v8a

# (str) The directory where buildozer will store the built packages
#buildozer.python.branch = 3.11

# (str) The directory where buildozer will store the built packages
#buildozer.python.commit = master

# (str) The directory where buildozer will store the built packages
#buildozer.python.implementation =cpython3

# (str) The directory where buildozer will store the built packages
#buildozer.python3 = True

# (str) The directory where buildozer will store the built packages
#buildozer.android.enable_androidx = True

# (str) The directory where buildozer will store the built packages
#buildozer.android.arch = armeabi-v7a
