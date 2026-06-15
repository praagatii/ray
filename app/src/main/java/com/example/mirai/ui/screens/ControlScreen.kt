package com.example.mirai.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.mirai.data.models.NexusStatsResponse
import com.example.mirai.ui.theme.*
import com.example.mirai.viewmodel.MiraiViewModel

@Composable
fun ControlScreen(
    serverConnected: Boolean,
    serverUrl: String,
    onServerUrlChange: (String) -> Unit,
    onLogout: () -> Unit,
    memoryEnabled: Boolean = true,
    onMemoryEnabledChange: () -> Unit = {},
    voiceEnabled: Boolean = true,
    onVoiceEnabledChange: () -> Unit = {},
    nexusStats: NexusStatsResponse? = null,
    viewModel: MiraiViewModel? = null
) {
    Column(modifier = Modifier.fillMaxSize().background(Background)) {
        Box(modifier = Modifier.fillMaxWidth().padding(top = 48.dp, bottom = 8.dp)) {
            Text("C O N T R O L", color = TextPrimary, fontSize = 10.sp, fontWeight = FontWeight.Light, letterSpacing = 5.sp,
                modifier = Modifier.align(Alignment.Center))
        }
        Column(
            modifier = Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(horizontal = 16.dp),
            verticalArrangement = Arrangement.spacedBy(10.dp)
        ) {
            SectionCard("connection") {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Box(modifier = Modifier.size(5.dp).clip(CircleShape).background(if (serverConnected) StatusOnline else StatusOffline))
                    Spacer(Modifier.width(8.dp))
                    Text(if (serverConnected) "connected" else "disconnected", color = TextPrimary, fontSize = 11.sp, fontWeight = FontWeight.Medium, letterSpacing = 0.3.sp)
                }
                Spacer(Modifier.height(8.dp))
                OutlinedTextField(value = serverUrl, onValueChange = onServerUrlChange,
                    label = { Text("server", color = TextMuted, fontSize = 9.sp) }, singleLine = true,
                    textStyle = LocalTextStyle.current.copy(color = TextPrimary, fontSize = 10.sp, letterSpacing = 0.3.sp),
                    colors = OutlinedTextFieldDefaults.colors(focusedTextColor = TextPrimary, unfocusedTextColor = TextPrimary, cursorColor = CyanGlow, focusedBorderColor = CyanGlow.copy(alpha = 0.25f), unfocusedBorderColor = CardBorder),
                    modifier = Modifier.fillMaxWidth().height(48.dp))
                if (viewModel != null) {
                    Spacer(Modifier.height(6.dp))
                    Button(onClick = { viewModel.testConnection() },
                        modifier = Modifier.fillMaxWidth().height(34.dp),
                        colors = ButtonDefaults.buttonColors(containerColor = CyanGlow.copy(alpha = 0.08f)),
                        shape = RoundedCornerShape(6.dp)) {
                        Text("test connection", color = CyanGlow, fontSize = 10.sp, letterSpacing = 0.5.sp)
                    }
                }
            }

            SectionCard("model") {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Column {
                        Text("AI model", color = TextPrimary, fontSize = 11.sp, fontWeight = FontWeight.Medium)
                        Text(if (serverConnected) "deepseek-v4-flash-free via OpenRouter" else "waiting for server", color = TextTertiary, fontSize = 8.sp, letterSpacing = 0.3.sp)
                    }
                }
            }

            SectionCard("voice") {
                Row(modifier = Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically) {
                    Column(modifier = Modifier.weight(1f)) {
                        Text("voice responses", color = TextPrimary, fontSize = 11.sp, fontWeight = FontWeight.Medium)
                        Text(if (voiceEnabled && (viewModel?.ttsReady == true)) "ready" else "off", color = TextTertiary, fontSize = 8.sp, letterSpacing = 0.3.sp)
                    }
                    Switch(checked = voiceEnabled, onCheckedChange = { onVoiceEnabledChange() },
                        colors = SwitchDefaults.colors(checkedThumbColor = CyanGlow, checkedTrackColor = CyanGlow.copy(alpha = 0.2f), uncheckedThumbColor = TextMuted, uncheckedTrackColor = CardBorder))
                }
            }

            SectionCard("memory") {
                Row(modifier = Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically) {
                    Column(modifier = Modifier.weight(1f)) {
                        Text("graph memory", color = TextPrimary, fontSize = 11.sp, fontWeight = FontWeight.Medium)
                        if (nexusStats != null) Text("${nexusStats.total_nodes} thoughts stored", color = TextTertiary, fontSize = 8.sp, letterSpacing = 0.3.sp)
                    }
                    Switch(checked = memoryEnabled, onCheckedChange = { onMemoryEnabledChange() },
                        colors = SwitchDefaults.colors(checkedThumbColor = CyanGlow, checkedTrackColor = CyanGlow.copy(alpha = 0.2f), uncheckedThumbColor = TextMuted, uncheckedTrackColor = CardBorder))
                }
            }

            SectionCard("debug") {
                val vm = viewModel
                if (vm != null) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Text("backend", color = TextTertiary, fontSize = 8.sp, modifier = Modifier.weight(1f), letterSpacing = 0.3.sp)
                        Text(if (serverConnected) "online" else "offline", color = if (serverConnected) StatusOnline else StatusOffline, fontSize = 9.sp, fontWeight = FontWeight.Medium)
                    }
                    Spacer(Modifier.height(2.dp))
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Text("url", color = TextTertiary, fontSize = 8.sp, modifier = Modifier.weight(1f), letterSpacing = 0.3.sp)
                        Text(vm.serverUrl, color = TextSecondary, fontSize = 7.sp)
                    }
                    Spacer(Modifier.height(2.dp))
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Text("voice", color = TextTertiary, fontSize = 8.sp, modifier = Modifier.weight(1f), letterSpacing = 0.3.sp)
                        Text(if (vm.ttsReady) "ready" else "init", color = if (vm.ttsReady) StatusOnline else TextMuted, fontSize = 9.sp)
                    }
                    Spacer(Modifier.height(2.dp))
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Text("error", color = TextTertiary, fontSize = 8.sp, modifier = Modifier.weight(1f), letterSpacing = 0.3.sp)
                        Text(vm.lastApiError?.message ?: "none", color = if (vm.lastApiError != null) StatusError else TextMuted, fontSize = 7.sp, maxLines = 2)
                    }
                    Spacer(Modifier.height(4.dp))
                    val pr = vm.probeResults
                    if (pr.isNotEmpty()) {
                        Text("last scan:", color = TextMuted, fontSize = 7.sp, letterSpacing = 0.3.sp)
                        pr.take(5).forEach { r ->
                            Row(verticalAlignment = Alignment.CenterVertically) {
                                Box(modifier = Modifier.size(3.dp).clip(CircleShape).background(if (r.success) StatusOnline else StatusError))
                                Spacer(Modifier.width(4.dp))
                                Text(r.url, color = TextTertiary, fontSize = 6.sp, modifier = Modifier.weight(1f))
                                Text("${r.latencyMs}ms", color = if (r.success) TextMuted else StatusError.copy(alpha = 0.6f), fontSize = 6.sp)
                            }
                        }
                    }
                    Spacer(Modifier.height(2.dp))
                    Text("nodes: ${nexusStats?.total_nodes ?: 0}  state: ${vm.uiState.name}", color = TextMuted, fontSize = 7.sp)
                    if (vm.crashLog.isNotBlank()) {
                        Spacer(Modifier.height(4.dp))
                        Text("crash: ${vm.crashLog}", color = StatusError.copy(alpha = 0.7f), fontSize = 6.sp, maxLines = 3)
                    }
                } else {
                    Text("no debug data", color = TextMuted, fontSize = 8.sp, letterSpacing = 0.3.sp)
                }
            }

            SectionCard("identity") {
                Text("Mirai v1.0", color = TextPrimary, fontSize = 11.sp, fontWeight = FontWeight.Medium)
                Spacer(Modifier.height(2.dp))
                Text("Ray  •  intelligence", color = TextTertiary, fontSize = 8.sp, letterSpacing = 0.3.sp)
                Spacer(Modifier.height(12.dp))
                Button(onClick = onLogout, modifier = Modifier.fillMaxWidth().height(34.dp),
                    colors = ButtonDefaults.buttonColors(containerColor = StatusError.copy(alpha = 0.1f)),
                    shape = RoundedCornerShape(6.dp)) {
                    Text("lock & exit", color = StatusError, fontSize = 10.sp, letterSpacing = 0.5.sp)
                }
            }
            Spacer(Modifier.height(64.dp))
        }
    }
}

@Composable
private fun SectionCard(title: String, content: @Composable ColumnScope.() -> Unit) {
    Column(
        modifier = Modifier.fillMaxWidth()
            .background(SurfaceLight, RoundedCornerShape(10.dp))
            .border(0.5.dp, CardBorder, RoundedCornerShape(10.dp))
            .padding(14.dp)
    ) {
        Text(title, color = TextMuted, fontSize = 7.sp, fontWeight = FontWeight.Medium, letterSpacing = 1.5.sp)
        Spacer(Modifier.height(6.dp))
        content()
    }
}
