package com.example.mirai.ui.theme

import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Typography
import androidx.compose.material3.darkColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.sp

private val MiraiDarkColorScheme = darkColorScheme(
    background = Background,
    surface = Surface,
    surfaceVariant = SurfaceLight,
    onBackground = TextPrimary,
    onSurface = TextPrimary,
    onSurfaceVariant = TextSecondary,
    primary = CyanGlow,
    onPrimary = Background,
    secondary = ElectricBlue,
    onSecondary = Background,
    tertiary = Violet,
    onTertiary = Background,
    error = StatusError,
    onError = TextPrimary,
    outline = CardBorder,
    outlineVariant = CardBorderLight
)

val MiraiTypography = Typography(
    bodyLarge = TextStyle(fontSize = 14.sp, letterSpacing = 0.5.sp, fontWeight = FontWeight.Light),
    bodyMedium = TextStyle(fontSize = 12.sp, letterSpacing = 0.5.sp, fontWeight = FontWeight.Light),
    bodySmall = TextStyle(fontSize = 11.sp, letterSpacing = 0.5.sp, fontWeight = FontWeight.Light),
    labelLarge = TextStyle(fontSize = 13.sp, letterSpacing = 1.sp, fontWeight = FontWeight.Light),
    labelMedium = TextStyle(fontSize = 11.sp, letterSpacing = 1.sp, fontWeight = FontWeight.Light),
    labelSmall = TextStyle(fontSize = 9.sp, letterSpacing = 1.5.sp, fontWeight = FontWeight.Light),
    titleLarge = TextStyle(fontSize = 16.sp, letterSpacing = 2.sp, fontWeight = FontWeight.Light),
    titleMedium = TextStyle(fontSize = 14.sp, letterSpacing = 1.5.sp, fontWeight = FontWeight.Light),
    titleSmall = TextStyle(fontSize = 12.sp, letterSpacing = 1.sp, fontWeight = FontWeight.Light)
)

@Composable
fun MiraiTheme(content: @Composable () -> Unit) {
    MaterialTheme(
        colorScheme = MiraiDarkColorScheme,
        typography = MiraiTypography,
        content = content
    )
}
