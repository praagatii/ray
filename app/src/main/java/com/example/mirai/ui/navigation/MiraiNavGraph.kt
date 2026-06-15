package com.example.mirai.ui.navigation

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.currentBackStackEntryAsState
import com.example.mirai.ui.screens.*
import com.example.mirai.ui.theme.*
import com.example.mirai.viewmodel.MiraiViewModel

sealed class Screen(val route: String) {
    data object Ray : Screen("ray")
    data object Mind : Screen("mind")
    data object Control : Screen("control")
}

val tabs = listOf(Screen.Ray, Screen.Mind, Screen.Control)

@Composable
fun MiraiNavGraph(navController: NavHostController, viewModel: MiraiViewModel = viewModel()) {
    val start = if (viewModel.isLoggedIn) Screen.Ray.route else "login"
    val navBackStackEntry by navController.currentBackStackEntryAsState()
    val currentRoute = navBackStackEntry?.destination?.route

    NavHost(navController = navController, startDestination = start) {
        composable("login") {
            LoginScreen(isFirstTime = viewModel.isFirstTime, onLogin = { pw ->
                viewModel.login(pw)
                if (viewModel.isLoggedIn) navController.navigate(Screen.Ray.route) { popUpTo("login") { inclusive = true } }
            }, error = viewModel.passwordError)
        }
        composable(Screen.Ray.route) { RayScreen(viewModel = viewModel) }
        composable(Screen.Mind.route) { MindScreen(viewModel = viewModel) }
        composable(Screen.Control.route) {
            ControlScreen(
                serverConnected = viewModel.serverConnected, serverUrl = viewModel.serverUrl,
                onServerUrlChange = { viewModel.updateServerUrl(it) },
                onLogout = { viewModel.logout(); navController.navigate("login") { popUpTo(0) { inclusive = true } } },
                memoryEnabled = viewModel.memoryEnabled, onMemoryEnabledChange = { viewModel.toggleMemory() },
                voiceEnabled = viewModel.voiceEnabled, onVoiceEnabledChange = { viewModel.toggleVoice() },
                nexusStats = viewModel.nexusStats, viewModel = viewModel
            )
        }
    }

    if (currentRoute in listOf(Screen.Ray.route, Screen.Mind.route, Screen.Control.route)) {
        Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.BottomCenter) {
            Surface(
                modifier = Modifier.padding(bottom = 20.dp).widthIn(max = 180.dp).height(48.dp)
                    .clip(RoundedCornerShape(24.dp)),
                shape = RoundedCornerShape(24.dp),
                color = Background.copy(alpha = 0.85f),
                tonalElevation = 0.dp,
                shadowElevation = 6.dp
            ) {
                Row(
                    modifier = Modifier.fillMaxWidth().padding(horizontal = 6.dp),
                    horizontalArrangement = Arrangement.SpaceEvenly,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    tabs.forEach { s ->
                        val sel = currentRoute == s.route
                        val icon = when (s) {
                            Screen.Ray -> "○"
                            Screen.Mind -> "✦"
                            Screen.Control -> "⌘"
                        }
                        val glow = if (sel) CyanGlow.copy(alpha = 0.2f) else Color.Transparent

                        Box(
                            modifier = Modifier
                                .size(44.dp)
                                .clip(RoundedCornerShape(22.dp))
                                .background(if (sel) CyanGlow.copy(alpha = 0.08f) else Color.Transparent)
                                .clickable {
                                    if (currentRoute != s.route) {
                                        navController.navigate(s.route) { launchSingleTop = true; restoreState = true }
                                    }
                                },
                            contentAlignment = Alignment.Center
                        ) {
                            Text(
                                icon,
                                color = if (sel) CyanGlow else TextMuted,
                                fontSize = 18.sp,
                                fontWeight = FontWeight.Light,
                                textAlign = TextAlign.Center
                            )
                        }
                    }
                }
            }
        }
    }
}
