package com.example.proyectoflask


import com.google.gson.annotations.SerializedName

data class LoginResponse(

    @SerializedName("message") val message: String,
    @SerializedName("access_token") val accessToken: String?
)
