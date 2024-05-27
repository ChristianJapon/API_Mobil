from flask import Flask
import os
import logging
import firebase_admin
from firebase_admin import credentials, firestore
from flask_jwt_extended import JWTManager

# Configuración de logging
logging.basicConfig(level=logging.DEBUG)

# Inicializar Firebase Admin
cred = credentials.Certificate('proyectoflask-47f4f-firebase-adminsdk-l8uq4-3b36e0d55f.json')
firebase_admin.initialize_app(cred)

# Obtén una referencia a la base de datos Firestore
db = firestore.client()

def create_app():
    app = Flask(__name__)
    
    # Configurar la clave secreta para JWT
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'password')
    
    # Inicializar JWT Manager
    jwt = JWTManager(app)

    # Importar y registrar los blueprints
    from .views import app_views  # Importación relativa porque `views.py` está en el mismo directorio
    app.register_blueprint(app_views, url_prefix='/api')

    return app

# Crear instancia de la aplicación
app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
