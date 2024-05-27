from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from PIL import Image
import io
import firebase_admin
from firebase_admin import firestore
from .filters import apply_filter

db = firestore.client()
app_views = Blueprint('app_views', __name__)

@app_views.route('/upload', methods=['POST'])
def upload_image():
    filter_type = request.form.get('filter', 'sepia')
    image_file = request.files['image']
    if not image_file:
        return jsonify({'error': 'No image file provided'}), 400

    image = Image.open(image_file.stream)
    filtered_image = apply_filter(image, filter_type)
    img_byte_arr = io.BytesIO()
    filtered_image.save(img_byte_arr, format='JPEG')
    img_byte_arr.seek(0)

    file_path = f'static/processed_{filter_type}.jpg'
    filtered_image.save(file_path)

    # Construir la URL completa para la imagen
    host_url = request.host_url.rstrip('/')
    image_url = f"{host_url}/static/processed_{filter_type}.jpg"

    try:
        new_image_ref = db.collection('processed_images').document()
        new_image_ref.set({
            'filter_type': filter_type,
            'image_path': file_path
        })
        return jsonify({'message': 'Image uploaded and processed successfully', 'image_url': image_url}), 201
    except Exception as e:
        current_app.logger.error(f"Failed to write to Firestore: {e}")
        return jsonify({'error': 'Failed to write to Firestore'}), 500

@app_views.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return jsonify({"message": "Email and password required"}), 400

    users_ref = db.collection('users')
    user_query = users_ref.where('email', '==', email).get()
    if list(user_query):
        return jsonify({"message": "User already exists"}), 409

    password_hash = generate_password_hash(password)
    try:
        new_user_ref = users_ref.document()
        new_user_ref.set({
            'email': email,
            'password_hash': password_hash
        })
        return jsonify({"message": "User created successfully"}), 201
    except Exception as e:
        current_app.logger.error(f"Failed to create user in Firestore: {e}")
        return jsonify({"error": "Failed to create user"}), 500

@app_views.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return jsonify({"message": "Email and password required"}), 400

    users_ref = db.collection('users')
    user_query = users_ref.where('email', '==', email).get()
    if not list(user_query) or not check_password_hash(list(user_query)[0].to_dict()['password_hash'], password):
        return jsonify({"message": "Invalid credentials"}), 401

    # Create a new access token for the authenticated user
    access_token = create_access_token(identity=email)
    return jsonify({"message": "Login successful", "access_token": access_token}), 200

@app_views.route('/users', methods=['GET'])
def get_users():
    users_ref = db.collection('users')
    docs = users_ref.stream()
    users_list = [doc.to_dict() for doc in docs]
    return jsonify(users_list), 200
