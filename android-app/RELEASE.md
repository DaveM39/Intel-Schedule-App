# Release Guide

## Branding

- Launcher label uses `Schedule & Tasks` to represent both app sections.
- Adaptive launcher icons now include standard, round, and Android 13 monochrome variants.
- The Play feature graphic is available at [marketing/feature-graphic.png](./marketing/feature-graphic.png) in the required 1024 x 500 format.

## Release Signing

The release build reads signing values from either:

- `keystore.properties` in the project root, or
- environment variables:
  - `ANDROID_KEYSTORE_PATH`
  - `ANDROID_KEYSTORE_PASSWORD`
  - `ANDROID_KEY_ALIAS`
  - `ANDROID_KEY_PASSWORD`

Start from [keystore.properties.example](./keystore.properties.example) and copy it to `keystore.properties` locally. Do not commit the real file.

Check whether signing is configured:

```bash
./gradlew printReleaseSigningStatus
```

Build a signed release APK:

```bash
./gradlew assembleRelease
```

Build a signed Android App Bundle for Play:

```bash
./gradlew bundleRelease
```

## Store Screenshots

Actual screenshots still need a running emulator or physical device. Capture at least these views:

1. Main planner with user name and cycle summary.
2. Day tab with color-coded activities.
3. Activity edit dialog.
4. Yearly calendar view.
5. Notes section with saved content.
6. Task chart summary and priority-sorted list.
7. Bottom navigation showing both Planner and Tasks.

Recommended workflow:

1. Run `./gradlew installDebug`.
2. Open the app on a phone-sized emulator.
3. Use `adb exec-out screencap -p > screenshot-01.png` for each target screen.
4. Save final captures under `marketing/screenshots/` when they are ready for review.

## Privacy Review

- Schedule and task data use app-private DataStore files.
- Cloud backup and device-to-device extraction rules exclude all app data.
- Schedule imports are capped at 1 MB and tolerate unknown fields for forward compatibility.
- No schedule payloads, keystores, or credentials belong in version control.
