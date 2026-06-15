package com.example.mirai.ui.screens

import androidx.compose.animation.core.*
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.Delete
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.*
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.mirai.data.models.NexusNode
import com.example.mirai.ui.theme.*
import com.example.mirai.viewmodel.MiraiViewModel
import kotlin.math.cos
import kotlin.math.sin
import kotlin.math.PI

@Composable
fun MindScreen(viewModel: MiraiViewModel) {
    val nodes = viewModel.graphNodes

    if (viewModel.selectedNode != null) {
        MindDetailView(viewModel = viewModel)
    } else if (nodes.isEmpty()) {
        MindEmptyState()
    } else {
        MindGraphView(viewModel = viewModel)
    }
}

@Composable
private fun MindEmptyState() {
    Box(modifier = Modifier.fillMaxSize().background(Background), contentAlignment = Alignment.Center) {
        Column(horizontalAlignment = Alignment.CenterHorizontally) {
            Text("R A Y ' S   M I N D", color = TextMuted, fontSize = 10.sp, letterSpacing = 4.sp)
            Spacer(Modifier.height(12.dp))
            Text("empty", color = TextTertiary, fontSize = 11.sp, letterSpacing = 1.sp)
            Spacer(Modifier.height(4.dp))
            Text("speak to create memories", color = TextMuted, fontSize = 8.sp, letterSpacing = 1.5.sp)
        }
    }
}

@Composable
private fun MindGraphView(viewModel: MiraiViewModel) {
    val nodes = viewModel.graphNodes
    val edges = viewModel.graphEdges

    val c = EdgesLayout.calculate(nodes)
    val centerNode = nodes.firstOrNull { it.type == "thought" || it.type == "memory" }
        ?: nodes.firstOrNull()

    Column(modifier = Modifier.fillMaxSize().background(Background)) {
        Box(modifier = Modifier.fillMaxWidth().padding(top = 48.dp, bottom = 8.dp)) {
            Text("R A Y ' S   M I N D", color = TextPrimary, fontSize = 10.sp, fontWeight = FontWeight.Light, letterSpacing = 5.sp,
                modifier = Modifier.align(Alignment.Center))
        }

        if (c.size < 2) {
            Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    RayMindOrb()
                    Spacer(Modifier.height(12.dp))
                    Text(nodes.firstOrNull()?.name ?: "one thought", color = TextSecondary, fontSize = 11.sp, letterSpacing = 0.5.sp)
                }
            }
        } else {
            val infinite = rememberInfiniteTransition(label = "mindOrbit")
            val orbitAngle by infinite.animateFloat(
                initialValue = 0f, targetValue = 360f,
                animationSpec = infiniteRepeatable(tween(8000, easing = LinearEasing), RepeatMode.Restart),
                label = "orbitAngle"
            )

            Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                Canvas(modifier = Modifier.fillMaxSize()) {
                    val cx = size.width / 2
                    val cy = size.height / 2
                    val r = minOf(cx, cy) * 0.5f

                    edges.forEach { edge ->
                        val src = nodes.find { it.id == edge.source_id }
                        val tgt = nodes.find { it.id == edge.target_id }
                        if (src != null && tgt != null) {
                            val si = nodes.indexOf(src)
                            val ti = nodes.indexOf(tgt)
                            val a1 = orbitAngle * (PI / 180f).toFloat() + si * 2f * PI.toFloat() / maxOf(1, c.size - 1)
                            val a2 = orbitAngle * (PI / 180f).toFloat() + ti * 2f * PI.toFloat() / maxOf(1, c.size - 1)
                            drawLine(
                                color = CardBorder.copy(alpha = 0.3f),
                                start = Offset(cx + cos(a1) * r, cy + sin(a1) * r),
                                end = Offset(cx + cos(a2) * r, cy + sin(a2) * r),
                                strokeWidth = 0.5f
                            )
                        }
                    }

                    nodes.forEachIndexed { i, node ->
                        val a = orbitAngle * (PI / 180f).toFloat() + i * 2f * PI.toFloat() / maxOf(1, c.size)
                        val nx = cx + cos(a) * r
                        val ny = cy + sin(a) * r
                        val pColor = when (node.type) {
                            "person" -> CyanGlow; "project" -> ElectricBlue; "idea" -> Violet
                            "memory" -> CyanGlow; "insight" -> Violet; "decision" -> ElectricBlue
                            else -> TextSecondary
                        }
                        drawCircle(pColor.copy(alpha = 0.6f), radius = 8f, center = Offset(nx, ny))
                    }
                }

                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    RayMindOrb(modifier = Modifier.size(64.dp))
                    Spacer(Modifier.height(8.dp))
                    Text("${nodes.size} memories", color = TextMuted, fontSize = 8.sp, letterSpacing = 1.sp)
                }
            }
        }

        if (nodes.size > 1) {
            Column(modifier = Modifier.fillMaxWidth().padding(horizontal = 24.dp, vertical = 8.dp)) {
                Text("nodes", color = TextMuted, fontSize = 7.sp, letterSpacing = 1.5.sp)
                Spacer(Modifier.height(4.dp))
                nodes.take(8).forEach { node ->
                    Row(
                        modifier = Modifier.fillMaxWidth().clickable { viewModel.selectNode(node) }.padding(vertical = 3.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        val dotColor = when (node.type) {
                            "person" -> CyanGlow; "project" -> ElectricBlue; "idea" -> Violet
                            "memory" -> CyanGlow; "insight" -> Violet; "decision" -> ElectricBlue
                            else -> TextSecondary
                        }
                        Box(modifier = Modifier.size(4.dp).clip(CircleShape).background(dotColor))
                        Spacer(Modifier.width(8.dp))
                        Text(node.name, color = TextSecondary, fontSize = 10.sp, maxLines = 1, overflow = TextOverflow.Ellipsis, modifier = Modifier.weight(1f))
                        Text(node.type, color = TextMuted, fontSize = 7.sp, letterSpacing = 0.5.sp)
                    }
                }
            }
        }
    }
}

@Composable
private fun MindDetailView(viewModel: MiraiViewModel) {
    val node = viewModel.selectedNode ?: return
    var showDeleteConfirm by remember { mutableStateOf(false) }

    if (showDeleteConfirm) {
        AlertDialog(
            onDismissRequest = { showDeleteConfirm = false },
            title = { Text("delete memory?", color = TextPrimary, fontSize = 13.sp) },
            text = { Text("\"${node.name.take(40)}\"", color = TextSecondary, fontSize = 11.sp) },
            confirmButton = {
                TextButton(onClick = {
                    showDeleteConfirm = false
                    viewModel.deleteNode(node.id)
                }) { Text("delete", color = StatusError, fontSize = 11.sp) }
            },
            dismissButton = {
                TextButton(onClick = { showDeleteConfirm = false }) { Text("cancel", color = TextMuted, fontSize = 11.sp) }
            },
            containerColor = SurfaceLight
        )
    }

    Column(modifier = Modifier.fillMaxSize().background(Background).padding(16.dp)) {
        Box(modifier = Modifier.fillMaxWidth().padding(top = 48.dp)) {
            Text("R A Y ' S   M I N D", color = TextPrimary, fontSize = 10.sp, fontWeight = FontWeight.Light, letterSpacing = 5.sp,
                modifier = Modifier.align(Alignment.Center))
            Row(modifier = Modifier.align(Alignment.CenterEnd)) {
                IconButton(onClick = { showDeleteConfirm = true }, modifier = Modifier.size(32.dp)) {
                    Icon(Icons.Filled.Delete, contentDescription = "Delete", tint = StatusError.copy(alpha = 0.7f), modifier = Modifier.size(15.dp))
                }
                IconButton(onClick = { viewModel.clearNodeSelection() }, modifier = Modifier.size(32.dp)) {
                    Icon(Icons.Filled.Close, contentDescription = "Close", tint = TextMuted, modifier = Modifier.size(16.dp))
                }
            }
        }
        Spacer(Modifier.height(24.dp))
        Box(modifier = Modifier.fillMaxWidth().clip(RoundedCornerShape(12.dp)).background(SurfaceLight).padding(16.dp)) {
            Column {
                val dotColor = when (node.type) {
                    "person" -> CyanGlow; "project" -> ElectricBlue; "idea" -> Violet
                    "memory" -> CyanGlow; "insight" -> Violet; "decision" -> ElectricBlue
                    else -> TextSecondary
                }
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Box(modifier = Modifier.size(6.dp).clip(CircleShape).background(dotColor))
                    Spacer(Modifier.width(8.dp))
                    Text(node.name, color = TextPrimary, fontSize = 13.sp, fontWeight = FontWeight.Medium)
                }
                Spacer(Modifier.height(4.dp))
                Text(node.type, color = dotColor.copy(alpha = 0.6f), fontSize = 9.sp, letterSpacing = 0.5.sp)
            }
        }
        Spacer(Modifier.height(16.dp))
        Text("connections (${viewModel.nodeConnections.size})", color = TextMuted, fontSize = 8.sp, letterSpacing = 1.sp)
        Spacer(Modifier.height(8.dp))
        if (viewModel.nodeConnections.isEmpty()) {
            Box(modifier = Modifier.fillMaxWidth().height(60.dp), contentAlignment = Alignment.Center) {
                Text("no connections", color = TextMuted, fontSize = 10.sp)
            }
        } else {
            viewModel.nodeConnections.forEach { conn ->
                val cn = conn["node"] as? Map<*, *>
                val et = conn["edge"] as? Map<*, *>
                val nn = cn?.get("name") as? String ?: "?"
                val nt = et?.get("type") as? String ?: "related_to"
                val nid = cn?.get("id") as? String ?: ""
                Box(modifier = Modifier.fillMaxWidth().clip(RoundedCornerShape(8.dp)).background(Surface).clickable {
                    if (nid.isNotEmpty()) viewModel.graphNodes.find { it.id == nid }?.let { viewModel.selectNode(it) }
                }.padding(10.dp)) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Text(nn, color = TextSecondary, fontSize = 11.sp, modifier = Modifier.weight(1f), maxLines = 1, overflow = TextOverflow.Ellipsis)
                        Text(nt, color = TextMuted, fontSize = 8.sp, letterSpacing = 0.3.sp)
                    }
                }
            }
        }
    }
}

@Composable
private fun RayMindOrb(modifier: Modifier = Modifier) {
    val infinite = rememberInfiniteTransition(label = "mindOrb")
    val pulse by infinite.animateFloat(
        initialValue = 0.95f, targetValue = 1.05f,
        animationSpec = infiniteRepeatable(tween(3000, easing = FastOutSlowInEasing), RepeatMode.Reverse),
        label = "pulse"
    )
    val glow by infinite.animateFloat(
        initialValue = 0.15f, targetValue = 0.4f,
        animationSpec = infiniteRepeatable(tween(2600, easing = FastOutSlowInEasing), RepeatMode.Reverse),
        label = "glow"
    )

    Canvas(modifier = modifier) {
        val cx = size.width / 2
        val cy = size.height / 2
        val r = minOf(cx, cy) * 0.4f * pulse

        drawCircle(
            brush = Brush.radialGradient(
                colors = listOf(CyanGlow.copy(alpha = glow * 0.5f), CyanGlow.copy(alpha = 0.1f), Color.Transparent),
                center = Offset(cx, cy), radius = r * 3f
            ), radius = r * 3f, center = Offset(cx, cy)
        )
        drawCircle(
            brush = Brush.radialGradient(
                colors = listOf(Color.Black.copy(alpha = 0.5f), Color.Black.copy(alpha = 0.8f), CyanGlow.copy(alpha = 0.2f)),
                center = Offset(cx - r * 0.2f, cy - r * 0.2f), radius = r * 1.4f
            ), radius = r, center = Offset(cx, cy)
        )
        drawCircle(color = CyanGlow.copy(alpha = glow * 0.3f), radius = r * 1.02f, center = Offset(cx, cy), style = Stroke(width = r * 0.06f))
        drawCircle(
            brush = Brush.radialGradient(
                colors = listOf(Color.White.copy(alpha = 0.2f), Color.Transparent),
                center = Offset(cx - r * 0.3f, cy - r * 0.3f), radius = r * 0.5f
            ), radius = r * 0.35f, center = Offset(cx - r * 0.3f, cy - r * 0.3f)
        )
    }
}

private object EdgesLayout {
    fun calculate(nodes: List<NexusNode>): List<NexusNode> = nodes
}
