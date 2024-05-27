package com.example.proyectoflask

import android.os.Bundle
import android.widget.ImageView
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import com.bumptech.glide.Glide

class ProfileActivity : AppCompatActivity() {

    private lateinit var username: TextView
    private lateinit var profileImage: ImageView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_profile)

        username = findViewById(R.id.username)
        profileImage = findViewById(R.id.profile_image)

        val imagePath = intent.getStringExtra("imagePath")

        // Aquí deberías obtener el nombre de usuario desde el servidor o una fuente de datos local
        username.text = "Usuario Ejemplo"

        if (imagePath != null) {
            val imageUrl = "http://192.168.154.130:5000/$imagePath" // Asegúrate de que la IP es accesible desde tu dispositivo Android
            Glide.with(this).load(imageUrl).into(profileImage)
        }

    }
}
