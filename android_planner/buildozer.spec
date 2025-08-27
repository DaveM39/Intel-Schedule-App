[app]
title = Intel Planner
package.name = intelplanner
package.domain = org.me
source.dir = .
source.include_exts = py,kv,json,png,jpg,atlas
requirements = python3,kivy==2.*,kivyMD,plyer
android.permissions = READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE
orientation = portrait

# (str) Supported orientation (one of: landscape, sensorLandscape, portrait or all)
# orientation = portrait

[buildozer]
log_level = 2
warn_on_root = 1
