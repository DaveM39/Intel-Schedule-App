# Repository Guidelines

## Project Structure & Module Organization
The project hosts a single Android application module under `app/`. Kotlin sources live in `app/src/main/java/com/example/schedule/`, with `MainActivity.kt` bootstrapping Compose UI, `ScheduleViewModel.kt` managing persistence, and UI building blocks grouped in `ui/` and `ui/theme/`. Declarative resources remain in `app/src/main/res/` (colors, strings, layouts). Top-level build configuration resides beside this document in `build.gradle.kts` and `settings.gradle.kts`.

## Build, Test, and Development Commands
Run Gradle tasks from this directory once the wrapper exists (`gradle wrapper` or open in Android Studio to generate `./gradlew`).
- `./gradlew assembleDebug` – compile and package the debug APK into `app/build/outputs/apk/debug/`.
- `./gradlew installDebug` – push the debug build to a connected emulator or device.
- `./gradlew lintDebug` – execute Android Lint and Compose checks.
- `./gradlew testDebugUnitTest` – run JVM unit tests.
- `./gradlew connectedDebugAndroidTest` – execute instrumentation tests; requires an emulator.

## Coding Style & Naming Conventions
Write Kotlin with Android Studio defaults: 4-space indentation, KDoc for public APIs, and trailing commas on multi-line argument lists. Prefer `PascalCase` for classes and composables, `camelCase` for functions and properties, and `CONSTANT_CASE` for constants. Compose preview functions should end with `Preview`. Keep stateful logic inside `ScheduleViewModel` and expose immutable UI state. Use `ktlint` or the IDE formatter before committing.

## Testing Guidelines
Place JVM unit tests under `app/src/test/java/com/example/schedule/` using JUnit4 + Truth (add dependencies if missing). Instrumented or Compose UI tests belong in `app/src/androidTest/java/`. Mirror production package names so tests share visibility. Cover schedule serialization, date-cycle math, and filtering rules. Run `lintDebug`, `testDebugUnitTest`, and (when UI changes) `connectedDebugAndroidTest` prior to opening a pull request.

## Commit & Pull Request Guidelines
Use imperative, 50-character summaries (e.g., `Add shift timeline screen`) with optional descriptive bodies wrapped at 72 characters. Group related changes per commit and avoid mixing formatting-only edits with functional work. For pull requests, provide a concise summary, highlight user-visible changes, list test evidence, attach emulator screenshots for UI updates, and link tracking issues. Keep branches rebased onto `main` and verify generated assets (e.g., JSON seeds) are excluded from version control.

## Environment Notes
Target Android Studio Giraffe (or newer) with SDK 33+. If `./gradlew` is absent, regenerate it before running tasks. Store secrets in local properties—never commit emulator keystores or JSON payloads containing personal data.
