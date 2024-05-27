package com.example.proyectoflask

import android.content.Intent
import android.os.Bundle
import android.provider.ContactsContract.CommonDataKinds.Website.URL
import android.widget.Button
import android.widget.EditText
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import okhttp3.ResponseBody
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import com.example.proyectoflask.ApiService
import com.google.gson.internal.bind.TypeAdapters.URL
import java.io.DataOutputStream
import java.net.HttpURLConnection
import java.net.URL

import java.net.URLEncoder


class MainActivity : AppCompatActivity() {

    private lateinit var email: EditText
    private lateinit var password: EditText

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        email = findViewById(R.id.email)
        password = findViewById(R.id.password)
        val registerButton: Button = findViewById(R.id.register)
        val loginButton: Button = findViewById(R.id.login)

        registerButton.setOnClickListener { registerUser() }
        loginButton.setOnClickListener { loginUser() }
    }

    private fun registerUser() {
        val thread = Thread {
            try {
                val url = URL("http://192.168.154.130:5000/api/register")
                val conn = url.openConnection() as HttpURLConnection
                conn.readTimeout = 10000
                conn.connectTimeout = 15000
                conn.requestMethod = "POST"
                conn.doInput = true
                conn.doOutput = true

                val postData: ByteArray = ("email=" + URLEncoder.encode(email.text.toString(), "UTF-8") +
                        "&password=" + URLEncoder.encode(password.text.toString(), "UTF-8")).toByteArray()

                conn.setRequestProperty("Content-Length", postData.size.toString())
                conn.setRequestProperty("Content-Type", "application/x-www-form-urlencoded")

                DataOutputStream(conn.outputStream).use { dos ->
                    dos.write(postData)
                }

                val responseCode = conn.responseCode

                runOnUiThread {
                    if (responseCode == HttpURLConnection.HTTP_OK) {
                        Toast.makeText(this, "Registration successful", Toast.LENGTH_SHORT).show()
                        startActivity(Intent(this, UploadImageActivity::class.java))
                    } else {
                        Toast.makeText(this, "Registration failed", Toast.LENGTH_SHORT).show()
                    }
                }
            } catch (e: Exception) {
                runOnUiThread {
                    Toast.makeText(this, "An error occurred: ${e.message}", Toast.LENGTH_SHORT).show()
                }
            }
        }
        thread.start()
    }

    private fun loginUser() {
        val thread = Thread {
            try {
                val url = URL("http://127.0.0.1:5000/api/login")
                val conn = url.openConnection() as HttpURLConnection
                conn.readTimeout = 100
                conn.connectTimeout = 15000
                conn.requestMethod = "POST"
                conn.doInput = true
                conn.doOutput = true

                val postData: ByteArray = ("email=" + URLEncoder.encode(email.text.toString(), "UTF-8") +
                        "&password=" + URLEncoder.encode(password.text.toString(), "UTF-8")).toByteArray()

                conn.setRequestProperty("Content-Length", postData.size.toString())
                conn.setRequestProperty("Content-Type", "application/x-www-form-urlencoded")

                DataOutputStream(conn.outputStream).use { dos ->
                    dos.write(postData)
                }

                val responseCode = conn.responseCode
                val responseMessage = conn.inputStream.bufferedReader().use { it.readText() } // Read the server response

                runOnUiThread {
                    if (responseCode == HttpURLConnection.HTTP_OK) {
                        Toast.makeText(this, "Login successful", Toast.LENGTH_SHORT).show()
                        val intent = Intent(this, UploadImageActivity::class.java)
                        intent.putExtra("token", responseMessage) // Assuming the token is the response
                        startActivity(intent)
                    } else {
                        Toast.makeText(this, "Login failed", Toast.LENGTH_SHORT).show()
                    }
                }
            } catch (e: Exception) {
                runOnUiThread {
                    val intent = Intent(this, UploadImageActivity::class.java)
                    //intent.putExtra("token", responseMessage) // Assuming the token is the response
                    startActivity(intent)
                    Toast.makeText(this, "An error occurred: ${e.message}", Toast.LENGTH_SHORT).show()
                }
            }
        }
        thread.start()
    }
}

