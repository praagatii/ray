package com.example.mirai.ui.screens

import android.Manifest
import android.content.pm.PackageManager
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.animation.*
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.core.content.ContextCompat
import com.example.mirai.ui.components.OrbState
import com.example.mirai.ui.components.RayOrb
import com.example.mirai.ui.theme.*
import com.example.mirai.viewmodel.MiraiViewModel
import com.example.mirai.viewmodel.UiState

@Composable
fun RayScreen(viewModel: MiraiViewModel) {
    val context = LocalContext.current
    var permissionDenied by remember { mutableStateOf(false) }

    val permissionLauncher = rememberLauncherForActivityResult(ActivityResultContracts.RequestPermission()) { granted ->
        if (granted) { permissionDenied = false; viewModel.startListening() }
        else { permissionDenied = true }
    }

    val orbState = when (viewModel.uiState) {
        UiState.IDLE -> OrbState.IDLE
        UiState.LISTENING -> OrbState.LISTENING
        UiState.THINKING -> OrbState.THINKING
        UiState.SPEAKING -> OrbState.SPEAKING
    }

    val statusText = when (viewModel.uiState) {
        UiState.IDLE -> if (viewModel.serverConnected) "" else "connecting"
        UiState.LISTENING -> "listening"
        UiState.THINKING -> "thinking"
        UiState.SPEAKING -> "speaking"
    }

    fun handleTap() {
        if (ContextCompat.checkSelfPermission(context, Manifest.permission.RECORD_AUDIO) == PackageManager.PERMISSION_GRANTED) {
            permissionDenied = false
            viewModel.tapOrb()
        } else {
            permissionLauncher.launch(Manifest.permission.RECORD_AUDIO)
        }
    }

    Box(
        modifier = Modifier.fillMaxSize().background(Background),
        contentAlignment = Alignment.Center
    ) {
        Column(horizontalAlignment = Alignment.CenterHorizontally) {

            Spacer(Modifier.weight(0.25f))

            Text("M I R A I", color = TextPrimary, fontSize = 12.sp, fontWeight = FontWeight.Light, letterSpacing = 8.sp)

            Spacer(Modifier.weight(0.3f))

            Box(
                modifier = Modifier.clip(CircleShape).clickable(enabled = viewModel.serverConnected) { handleTap() }
            ) {
                RayOrb(state = orbState, size = 160.dp)
            }

            Spacer(Modifier.height(20.dp))

            AnimatedVisibility(visible = viewModel.uiState == UiState.LISTENING && viewModel.transcript.isNotEmpty()) {
                Text(viewModel.transcript, color = TextSecondary, fontSize = 13.sp, textAlign = TextAlign.Center,
                    modifier = Modifier.padding(horizontal = 40.dp), lineHeight = 20.sp)
            }

            AnimatedVisibility(visible = viewModel.uiState == UiState.SPEAKING && viewModel.lastResponse.isNotEmpty()) {
                Text(viewModel.lastResponse, color = TextSecondary, fontSize = 12.sp, textAlign = TextAlign.Center,
                    modifier = Modifier.padding(horizontal = 40.dp), lineHeight = 18.sp)
            }

            if (viewModel.lastResponse.isNotEmpty() && viewModel.uiState == UiState.IDLE) {
                Text(viewModel.lastResponse, color = TextSecondary, fontSize = 12.sp, textAlign = TextAlign.Center,
                    modifier = Modifier.padding(horizontal = 40.dp), lineHeight = 18.sp)
            }

            if (permissionDenied) {
                Spacer(Modifier.height(8.dp))
                Text("mic permission required", color = StatusError, fontSize = 10.sp, letterSpacing = 1.sp)
            }

            Spacer(Modifier.weight(0.35f))

            if (viewModel.uiState == UiState.IDLE && viewModel.serverConnected) {
                Text("hey ray...", color = TextMuted, fontSize = 10.sp, letterSpacing = 3.sp)
            }

            if (!viewModel.serverConnected) {
                Spacer(Modifier.height(6.dp))
                Text(statusText, color = TextTertiary, fontSize = 9.sp, letterSpacing = 1.5.sp)
            }

            Spacer(Modifier.height(32.dp))
        }
    }
}
