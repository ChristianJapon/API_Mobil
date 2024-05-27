# Usar una imagen base con CUDA para soporte de GPU
FROM nvidia/cuda:12.1.0-devel-ubuntu22.04

# Instalar Python y otras dependencias necesarias
RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-dev \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-setuptools \
    && ln -s /usr/bin/python3 /usr/bin/python \
    && rm -rf /var/lib/apt/lists/*

# Actualizar pip
RUN pip install --upgrade pip

# Configurar el entorno de trabajo
WORKDIR /app

# Instalar las dependencias de Python
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el directorio del proyecto
COPY . /app

# Exponer el puerto usado por la aplicación
EXPOSE 5000

# Comando para ejecutar la aplicación
CMD ["flask", "run", "--host=0.0.0.0"]
