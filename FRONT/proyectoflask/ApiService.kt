package com.example.proyectoflask

import okhttp3.MultipartBody
import okhttp3.RequestBody
import okhttp3.ResponseBody
import retrofit2.Call
import retrofit2.http.Body
import retrofit2.http.Multipart
import retrofit2.http.POST
import retrofit2.http.Part

interface ApiService {

    data class LoginRequest(
        val email: String,
        val password: String
    )


    @POST("api/register")
    fun registerUser(@Body user: User): Call<ResponseBody>

    @POST("api/login")
    fun loginUser(@Body loginRequest: LoginRequest): Call<LoginResponse>

    @Multipart
    @POST("api/upload")
    fun uploadImage(
        @Part image: MultipartBody.Part,
        @Part("filter") filter: RequestBody
    ): Call<ResponseBody>

}