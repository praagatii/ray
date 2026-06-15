package com.example.mirai.ui.components

import androidx.compose.animation.core.*
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.layout.size
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.*
import androidx.compose.ui.graphics.drawscope.DrawScope
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import com.example.mirai.ui.theme.*
import kotlin.math.cos
import kotlin.math.sin
import kotlin.math.PI

enum class OrbState { IDLE, LISTENING, THINKING, SPEAKING }

@Composable
fun RayOrb(
    state: OrbState = OrbState.IDLE,
    size: Dp = 160.dp,
    modifier: Modifier = Modifier
) {
    val infinite = rememberInfiniteTransition(label = "orb")

    val breathe by infinite.animateFloat(
        initialValue = 0.96f, targetValue = 1.04f,
        animationSpec = infiniteRepeatable(tween(3000, easing = FastOutSlowInEasing), RepeatMode.Reverse),
        label = "breathe"
    )
    val listenPulse by infinite.animateFloat(
        initialValue = 0.9f, targetValue = 1.15f,
        animationSpec = infiniteRepeatable(tween(800, easing = EaseInOutCubic), RepeatMode.Reverse),
        label = "listenPulse"
    )
    val listenRing by infinite.animateFloat(
        initialValue = 0f, targetValue = 1f,
        animationSpec = infiniteRepeatable(tween(1200, easing = LinearEasing), RepeatMode.Restart),
        label = "listenRing"
    )
    val thinkAngle by infinite.animateFloat(
        initialValue = 0f, targetValue = 360f,
        animationSpec = infiniteRepeatable(tween(5000, easing = LinearEasing), RepeatMode.Restart),
        label = "thinkAngle"
    )
    val thinkPulse by infinite.animateFloat(
        initialValue = 0.95f, targetValue = 1.08f,
        animationSpec = infiniteRepeatable(tween(1800, easing = FastOutSlowInEasing), RepeatMode.Reverse),
        label = "thinkPulse"
    )
    val speakWave by infinite.animateFloat(
        initialValue = 0f, targetValue = 1f,
        animationSpec = infiniteRepeatable(tween(600, easing = LinearEasing), RepeatMode.Restart),
        label = "speakWave"
    )
    val glowAlpha by infinite.animateFloat(
        initialValue = 0.2f, targetValue = 0.55f,
        animationSpec = infiniteRepeatable(tween(2600, easing = FastOutSlowInEasing), RepeatMode.Reverse),
        label = "glowAlpha"
    )

    Canvas(modifier = modifier.size(size)) {
        val cx = size.toPx() / 2
        val cy = size.toPx() / 2
        val base = size.toPx() * 0.3f

        when (state) {
            OrbState.IDLE -> drawIdle(cx, cy, base, breathe, glowAlpha)
            OrbState.LISTENING -> drawListening(cx, cy, base, listenPulse, listenRing, glowAlpha)
            OrbState.THINKING -> drawThinking(cx, cy, base, thinkPulse, thinkAngle, glowAlpha)
            OrbState.SPEAKING -> drawSpeaking(cx, cy, base, speakWave, glowAlpha)
        }
    }
}

private fun DrawScope.drawIdle(cx: Float, cy: Float, r: Float, pulse: Float, ga: Float) {
    val radius = r * pulse
    outerGlow(cx, cy, radius * 2.8f, CyanGlow.copy(alpha = ga * 0.3f))
    glassSphere(cx, cy, radius, CyanGlow.copy(alpha = 0.15f))
    edgeGlow(cx, cy, radius, CyanGlow.copy(alpha = ga * 0.4f))
    edgeGlow(cx, cy, radius * 0.85f, Violet.copy(alpha = ga * 0.2f))
    specularHighlight(cx, cy, radius)
}

private fun DrawScope.drawListening(cx: Float, cy: Float, r: Float, pulse: Float, ringPhase: Float, ga: Float) {
    val radius = r * pulse
    outerGlow(cx, cy, radius * 3.2f, CyanGlow.copy(alpha = ga * 0.5f))
    glassSphere(cx, cy, radius, CyanGlow.copy(alpha = 0.3f))
    edgeGlow(cx, cy, radius, CyanGlow.copy(alpha = ga * 0.8f))
    specularHighlight(cx, cy, radius)

    rippleRing(cx, cy, radius * 1.3f, ringPhase, CyanGlow.copy(alpha = 0.5f))
    rippleRing(cx, cy, radius * 1.6f, (ringPhase + 0.4f).let { if (it > 1f) it - 1f else it }, CyanGlow.copy(alpha = 0.3f))
    rippleRing(cx, cy, radius * 1.9f, (ringPhase + 0.7f).let { if (it > 1f) it - 1f else it }, CyanGlow.copy(alpha = 0.15f))
}

private fun DrawScope.drawThinking(cx: Float, cy: Float, r: Float, pulse: Float, angle: Float, ga: Float) {
    val radius = r * pulse
    outerGlow(cx, cy, radius * 2.8f, Violet.copy(alpha = ga * 0.4f))
    glassSphere(cx, cy, radius, Violet.copy(alpha = 0.2f))
    edgeGlow(cx, cy, radius, Violet.copy(alpha = ga * 0.5f))
    edgeGlow(cx, cy, radius * 0.85f, CyanGlow.copy(alpha = ga * 0.25f))
    specularHighlight(cx, cy, radius)

    val particleCount = 6
    repeat(particleCount) { i ->
        val a = angle * (PI / 180f).toFloat() + i * 60f * (PI / 180f).toFloat()
        val orbitR = radius * (1.5f + 0.15f * sin((angle * 2f) * (PI / 180f).toFloat()))
        val px = cx + cos(a) * orbitR
        val py = cy + sin(a) * orbitR
        val pSize = radius * (0.04f + 0.03f * (0.5f + 0.5f * sin(a * 2f)))
        val pColor = if (i % 2 == 0) CyanGlow else Violet
        drawCircle(pColor.copy(alpha = 0.7f * ga), radius = pSize, center = Offset(px, py))
    }

    repeat(2) { i ->
        val ringR = radius * (1.3f + i * 0.35f)
        val ringAngle = angle * (PI / 180f).toFloat() + i * 90f * (PI / 180f).toFloat()
        val ringColor = if (i == 0) CyanGlow else Violet
        ring(cx, cy, ringR, ringColor.copy(alpha = ga * 0.2f), radius * 0.025f)
    }
}

private fun DrawScope.drawSpeaking(cx: Float, cy: Float, r: Float, wave: Float, ga: Float) {
    val radius = r * 0.95f
    outerGlow(cx, cy, radius * 3f, CyanGlow.copy(alpha = ga * 0.45f))
    glassSphere(cx, cy, radius, CyanGlow.copy(alpha = 0.35f))
    edgeGlow(cx, cy, radius, CyanGlow.copy(alpha = ga * 0.7f))
    specularHighlight(cx, cy, radius)

    val bars = 9
    val bw = radius * 0.25f / bars
    val maxH = radius * 1.4f
    val spacing = radius * 0.4f / bars
    val startX = cx - radius * 0.3f

    repeat(bars) { i ->
        val phase = i.toFloat() / bars
        val bh = maxH * (0.1f + 0.9f * maxOf(0f, sin(wave * 2f * PI.toFloat() * 2f + phase * 2f * PI.toFloat())))
        val alpha = 0.2f + 0.8f * (bh / maxH)
        drawRoundRect(
            color = CyanGlow.copy(alpha = alpha * ga * 1.2f),
            topLeft = Offset(startX + i * (bw + spacing), cy - bh / 2),
            size = androidx.compose.ui.geometry.Size(bw, bh),
            cornerRadius = androidx.compose.ui.geometry.CornerRadius(bw / 2, bw / 2)
        )
    }
}

private fun DrawScope.outerGlow(cx: Float, cy: Float, r: Float, color: Color) {
    drawCircle(
        brush = Brush.radialGradient(
            colors = listOf(color, color.copy(alpha = 0.15f), Color.Transparent),
            center = Offset(cx, cy), radius = r
        ), radius = r, center = Offset(cx, cy)
    )
}

private fun DrawScope.glassSphere(cx: Float, cy: Float, r: Float, edgeColor: Color) {
    drawCircle(
        brush = Brush.radialGradient(
            colors = listOf(Color.Black.copy(alpha = 0.6f), Color.Black.copy(alpha = 0.85f), edgeColor),
            center = Offset(cx - r * 0.25f, cy - r * 0.25f), radius = r * 1.4f
        ), radius = r, center = Offset(cx, cy)
    )
}

private fun DrawScope.edgeGlow(cx: Float, cy: Float, r: Float, color: Color) {
    drawCircle(
        brush = Brush.radialGradient(
            colors = listOf(Color.Transparent, Color.Transparent, color),
            center = Offset(cx, cy), radius = r
        ), radius = r * 1.02f, center = Offset(cx, cy), style = Stroke(width = r * 0.08f)
    )
    drawCircle(color = color.copy(alpha = 0.2f), radius = r, center = Offset(cx, cy), style = Stroke(width = r * 0.03f))
}

private fun DrawScope.specularHighlight(cx: Float, cy: Float, r: Float) {
    val hx = cx - r * 0.3f
    val hy = cy - r * 0.3f
    drawCircle(
        brush = Brush.radialGradient(
            colors = listOf(Color.White.copy(alpha = 0.25f), Color.Transparent),
            center = Offset(hx, hy), radius = r * 0.5f
        ), radius = r * 0.4f, center = Offset(hx, hy)
    )
    val hx2 = cx - r * 0.2f
    val hy2 = cy - r * 0.25f
    drawCircle(
        brush = Brush.radialGradient(
            colors = listOf(Color.White.copy(alpha = 0.1f), Color.Transparent),
            center = Offset(hx2, hy2), radius = r * 0.3f
        ), radius = r * 0.25f, center = Offset(hx2, hy2)
    )
}

private fun DrawScope.rippleRing(cx: Float, cy: Float, r: Float, phase: Float, color: Color) {
    val alpha = 1f - phase
    val ringR = r * (0.8f + 0.2f * phase)
    drawCircle(color = color.copy(alpha = alpha * 0.4f), radius = ringR, center = Offset(cx, cy), style = Stroke(width = r * 0.04f * (1f - phase * 0.5f)))
}

private fun DrawScope.ring(cx: Float, cy: Float, r: Float, color: Color, width: Float) {
    drawCircle(color = color, radius = r, center = Offset(cx, cy), style = Stroke(width = width))
}
