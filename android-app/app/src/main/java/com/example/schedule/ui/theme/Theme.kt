package com.example.schedule.ui.theme

import android.os.Build
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Typography
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.dynamicDarkColorScheme
import androidx.compose.material3.dynamicLightColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext

private val LightColorScheme = lightColorScheme(
    primary = Color(0xFF0F5EA8),
    onPrimary = Color(0xFFFFFFFF),
    primaryContainer = Color(0xFFD7E9FF),
    onPrimaryContainer = Color(0xFF001C36),
    secondary = Color(0xFF8D5D00),
    onSecondary = Color(0xFFFFFFFF),
    secondaryContainer = Color(0xFFFFDEA9),
    onSecondaryContainer = Color(0xFF2D1A00),
    tertiary = Color(0xFF2F6F4F),
    onTertiary = Color(0xFFFFFFFF),
    tertiaryContainer = Color(0xFFB3F0CA),
    onTertiaryContainer = Color(0xFF002113),
    background = Color(0xFFF4F7FB),
    onBackground = Color(0xFF171C22),
    surface = Color(0xFFFBFCFF),
    onSurface = Color(0xFF171C22),
    surfaceVariant = Color(0xFFDCE3EE),
    onSurfaceVariant = Color(0xFF404854),
    outline = Color(0xFF707985),
    error = Color(0xFFBA1A1A),
    onError = Color(0xFFFFFFFF)
)

private val DarkColorScheme = darkColorScheme(
    primary = Color(0xFFA8CBFF),
    onPrimary = Color(0xFF00315C),
    primaryContainer = Color(0xFF004881),
    onPrimaryContainer = Color(0xFFD7E9FF),
    secondary = Color(0xFFFFB950),
    onSecondary = Color(0xFF4B2F00),
    secondaryContainer = Color(0xFF6B4400),
    onSecondaryContainer = Color(0xFFFFDEA9),
    tertiary = Color(0xFF97D3AF),
    onTertiary = Color(0xFF003823),
    tertiaryContainer = Color(0xFF175139),
    onTertiaryContainer = Color(0xFFB3F0CA),
    background = Color(0xFF101419),
    onBackground = Color(0xFFE0E6EE),
    surface = Color(0xFF11181F),
    onSurface = Color(0xFFE0E6EE),
    surfaceVariant = Color(0xFF404854),
    onSurfaceVariant = Color(0xFFC0C7D2),
    outline = Color(0xFF8A93A0),
    error = Color(0xFFFFB4AB),
    onError = Color(0xFF690005)
)

@Composable
fun ScheduleTheme(
    darkTheme: Boolean,
    content: @Composable () -> Unit
) {
    val colorScheme = when {
        Build.VERSION.SDK_INT >= Build.VERSION_CODES.S -> {
            val context = LocalContext.current
            if (darkTheme) dynamicDarkColorScheme(context) else dynamicLightColorScheme(context)
        }
        darkTheme -> DarkColorScheme
        else -> LightColorScheme
    }

    MaterialTheme(
        colorScheme = colorScheme,
        typography = Typography(),
        content = content
    )
}
