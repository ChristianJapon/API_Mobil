package com.example.proyectoflask

import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.provider.MediaStore
import android.widget.Button
import android.widget.ImageView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.bumptech.glide.Glide
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.MultipartBody
import okhttp3.RequestBody
import okhttp3.ResponseBody
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.io.File
import java.io.FileOutputStream

class UploadImageActivity : AppCompatActivity() {

    private val PICK_IMAGE = 1
    private lateinit var imageView: ImageView
    private var imageUri: Uri? = null

    private lateinit var retrofit: Retrofit
    private lateinit var apiService: ApiService

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_upload_image)

        imageView = findViewById(R.id.imageView)
        val selectImageButton: Button = findViewById(R.id.select_image)
        val applyFilterButton: Button = findViewById(R.id.apply_filter)

        // Configure Retrofit instance
        retrofit = Retrofit.Builder()
            .baseUrl("http://192.168.154.130:5000/") // Ensure this URL is correct for your local server
            .addConverterFactory(GsonConverterFactory.create())
            .build()

        apiService = retrofit.create(ApiService::class.java)

        selectImageButton.setOnClickListener { pickImage() }
        applyFilterButton.setOnClickListener { uploadImage() }
    }

    private fun pickImage() {
        val intent = Intent(Intent.ACTION_PICK, MediaStore.Images.Media.EXTERNAL_CONTENT_URI)
        startActivityForResult(intent, PICK_IMAGE)
    }

    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        if (requestCode == PICK_IMAGE && resultCode == RESULT_OK && data != null) {
            imageUri = data.data
            Glide.with(this).load(imageUri).into(imageView)
        }
    }

    private fun uploadImage() {
        imageUri?.let { uri ->
            val inputStream = contentResolver.openInputStream(uri)
            val file = File(cacheDir, "temp_image.jpg") // Create a temp file
            val outputStream = FileOutputStream(file)
            inputStream?.copyTo(outputStream)

            val requestBody = RequestBody.create("image/jpeg".toMediaTypeOrNull(), file)
            val imagePart = MultipartBody.Part.createFormData("image", file.name, requestBody)

            val filterType = "anamorphic" // The filter type you want to apply
            val filterPart = RequestBody.create("text/plain".toMediaTypeOrNull(), filterType)

            apiService.uploadImage(imagePart, filterPart).enqueue(object : Callback<ResponseBody> {
                override fun onResponse(call: Call<ResponseBody>, response: Response<ResponseBody>) {
                    if (response.isSuccessful) {
                        Toast.makeText(this@UploadImageActivity, "Image uploaded successfully", Toast.LENGTH_SHORT).show()
                    } else {
                        Toast.makeText(this@UploadImageActivity, "Failed to upload image", Toast.LENGTH_SHORT).show()
                    }
                }

                override fun onFailure(call: Call<ResponseBody>, t: Throwable) {
                    Toast.makeText(this@UploadImageActivity, "Error: ${t.message}", Toast.LENGTH_SHORT).show()
                }
            })

            // Clean up
            inputStream?.close()
            outputStream.close()
            file.delete() // Optionally, delete the temp file after uploading
        } ?: Toast.makeText(this, "No image selected", Toast.LENGTH_SHORT).show()
    }
}
