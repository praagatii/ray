package com.example.mirai.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Psychology
import androidx.compose.material.icons.filled.Visibility
import androidx.compose.material.icons.filled.VisibilityOff
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.text.input.VisualTransformation
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.mirai.ui.theme.*

@Composable
fun LoginScreen(
    isFirstTime: Boolean,
    onLogin: (String) -> Unit,
    error: String = ""
) {
    var password by remember { mutableStateOf("") }
    var confirmPassword by remember { mutableStateOf("") }
    var showPassword by remember { mutableStateOf(false) }
    var localError by remember { mutableStateOf("") }

    val displayError = error.ifEmpty { localError }

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(Background),
        contentAlignment = Alignment.Center
    ) {
        Column(
            horizontalAlignment = Alignment.CenterHorizontally,
            modifier = Modifier
                .width(320.dp)
                .background(CardBackground, RoundedCornerShape(20.dp))
                .border(0.5.dp, GlassBorder, RoundedCornerShape(20.dp))
                .padding(32.dp)
        ) {
            Icon(
                Icons.Filled.Psychology,
                contentDescription = null,
                tint = MutedGreen,
                modifier = Modifier.size(48.dp)
            )

            Spacer(Modifier.height(16.dp))

            Text(
                "MIRAI",
                color = TextPrimary,
                fontSize = 28.sp,
                fontWeight = FontWeight.Bold,
                letterSpacing = 4.sp
            )

            Text(
                "Your second brain",
                color = TextSecondary,
                fontSize = 12.sp
            )

            Spacer(Modifier.height(32.dp))

            if (isFirstTime) {
                Text("Create your password", color = TextMuted, fontSize = 11.sp)
                Spacer(Modifier.height(12.dp))
            }

            OutlinedTextField(
                value = password,
                onValueChange = {
                    password = it
                    localError = ""
                },
                label = { Text(if (isFirstTime) "New Password" else "Password", color = TextMuted, fontSize = 12.sp) },
                visualTransformation = if (showPassword) VisualTransformation.None else PasswordVisualTransformation(),
                trailingIcon = {
                    IconButton(onClick = { showPassword = !showPassword }) {
                        Icon(
                            if (showPassword) Icons.Filled.VisibilityOff else Icons.Filled.Visibility,
                            contentDescription = null,
                            tint = TextMuted
                        )
                    }
                },
                singleLine = true,
                colors = OutlinedTextFieldDefaults.colors(
                    focusedTextColor = TextPrimary,
                    unfocusedTextColor = TextPrimary,
                    cursorColor = MutedGreen,
                    focusedBorderColor = MutedGreen,
                    unfocusedBorderColor = CardBorder
                ),
                keyboardOptions = KeyboardOptions(imeAction = ImeAction.Next),
                modifier = Modifier.fillMaxWidth()
            )

            if (isFirstTime) {
                Spacer(Modifier.height(12.dp))
                OutlinedTextField(
                    value = confirmPassword,
                    onValueChange = { confirmPassword = it; localError = "" },
                    label = { Text("Confirm Password", color = TextMuted, fontSize = 12.sp) },
                    visualTransformation = if (showPassword) VisualTransformation.None else PasswordVisualTransformation(),
                    singleLine = true,
                    colors = OutlinedTextFieldDefaults.colors(
                        focusedTextColor = TextPrimary,
                        unfocusedTextColor = TextPrimary,
                        cursorColor = MutedGreen,
                        focusedBorderColor = MutedGreen,
                        unfocusedBorderColor = CardBorder
                    ),
                    keyboardOptions = KeyboardOptions(imeAction = ImeAction.Done),
                    keyboardActions = KeyboardActions(onDone = {
                        if (isFirstTime && password.length < 4) {
                            localError = "Password must be at least 4 characters"
                        } else if (isFirstTime && password != confirmPassword) {
                            localError = "Passwords do not match"
                        } else {
                            onLogin(password)
                        }
                    }),
                    modifier = Modifier.fillMaxWidth()
                )
            }

            if (displayError.isNotEmpty()) {
                Spacer(Modifier.height(8.dp))
                Text(displayError, color = WineRed, fontSize = 11.sp, textAlign = TextAlign.Center)
            }

            Spacer(Modifier.height(20.dp))

            Button(
                onClick = {
                    if (isFirstTime && password.length < 4) {
                        localError = "Password must be at least 4 characters"
                    } else if (isFirstTime && password != confirmPassword) {
                        localError = "Passwords do not match"
                    } else {
                        onLogin(password)
                    }
                },
                modifier = Modifier.fillMaxWidth().height(44.dp),
                colors = ButtonDefaults.buttonColors(
                    containerColor = MutedGreen,
                    contentColor = Background
                ),
                shape = RoundedCornerShape(12.dp)
            ) {
                Text(
                    if (isFirstTime) "Create & Enter" else "Unlock",
                    fontWeight = FontWeight.Medium,
                    fontSize = 14.sp
                )
            }
        }
    }
}
