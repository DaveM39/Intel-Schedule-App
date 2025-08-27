# Intel Planner (KivyMD)

This folder contains a **work in progress** port of the original
Tkinter-based Intel technician planner to [Kivy](https://kivy.org) and
[KivyMD](https://kivymd.readthedocs.io/).  The goal is to run entirely on
Android devices with offline persistence.

## Running on desktop

```bash
python main.py
```

The application uses the user specific storage directory provided by
Kivy (`App.user_data_dir`) to save `schedule.json`.

## Android build

The project is prepared for [Buildozer](https://github.com/kivy/buildozer).
A minimal `buildozer.spec` is included.  Typical build commands are:

```bash
python -m pip install -U buildozer cython
buildozer init          # only required once
buildozer android debug
# Optional: deploy to a connected device
# buildozer android deploy run
```

The `requirements` field already contains the required dependencies:
`python3,kivy==2.*,kivyMD,plyer`.

## Data storage

Schedule information is stored in `schedule.json` under the app's
`user_data_dir`.  A default schedule is bundled in
`app/default_schedule.json` and is copied to the user directory on first
launch.

## Status

This is a skeleton implementation intended as a starting point.  Some
features from the desktop version (legend filtering, yearly calendar,
import/export) are not yet implemented.
