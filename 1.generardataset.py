import pandas as pd
import random
from datetime import datetime, timedelta
import hashlib
import os

# Función para generar IP aleatoria
def random_ip():
    return ".".join(str(random.randint(1, 255)) for _ in range(4))

# Función para generar hash aleatorio
def random_hash():
    return hashlib.md5(str(random.randint(1000, 9999)).encode()).hexdigest()

# Listas de dominios y eventos
dominios_maliciosos = ["malware.example.com", "suspicious.net", "phishing.attack.org", "trojan.download.site"]
dominios_benignos = ["benign.example.com", "safe.domain.net", "trusted.source.org"]

eventos_maliciosos = ["Acceso no autorizado", "Autenticación fallida", "Transferencia de datos sospechosa", "Descarga de malware"]
eventos_benignos = ["Acceso autorizado", "Operación normal", "Transferencia legítima"]

descripciones_maliciosas = [
    "Acceso inusual en horario no laboral", "Múltiples intentos de login fallidos", "Actividad sospechosa detectada",
    "Archivo ejecutable descargado de fuente no confiable"
]
descripciones_benignas = [
    "Acceso realizado en horario habitual", "Operación esperada dentro de red segura", "Transferencia de datos sin anomalías"
]

# Pedir cantidad de registros
while True:
    try:
        cantidad_registros = int(input("¿Cuántos registros desea crear? (1-1000): "))
        if 1 <= cantidad_registros <= 1000:
            break
        else:
            print("Por favor, ingrese un número entre 1 y 1000.")
    except ValueError:
        print("Entrada no válida. Ingrese un número entero.")

# Crear dataset
data = []
start_time = datetime(2025, 1, 15, 0, 0, 0)
for _ in range(cantidad_registros):
    timestamp = start_time + timedelta(minutes=random.randint(1, 5000))
    origen_IP = random_ip()
    destino_IP = random_ip()
    hash_archivo = random_hash() if random.random() > 0.3 else ""  # Algunos registros sin hash
    if random.random() > 0.6:  # 60% de eventos maliciosos
        dominio = random.choice(dominios_maliciosos)
        evento = random.choice(eventos_maliciosos)
        descripcion = random.choice(descripciones_maliciosas)
    else:
        dominio = random.choice(dominios_benignos)
        evento = random.choice(eventos_benignos)
        descripcion = random.choice(descripciones_benignas)
    
    data.append([timestamp, origen_IP, destino_IP, hash_archivo, dominio, evento, descripcion])

# Crear DataFrame
df = pd.DataFrame(data, columns=["timestamp", "origen_IP", "destino_IP", "hash_archivo", "dominio", "evento", "descripcion"])

# Mostrar los primeros 5 registros
print("\nDatos generados:")
print(df.columns.tolist())  # Mostrar los nombres de las columnas
print(df.head(5).to_string(index=False))  # Mostrar los primeros 5 registros sin índice

# Menú de opciones
while True:
    print("\nMenú:")
    print("1. Guardar el archivo")
    print("2. Mostrar todos los registros")
    print("3. No guardar los registros y salir")
    
    opcion = input("Seleccione una opción: ")
    
    if opcion == "1":
        file_name = input("Ingrese el nombre del archivo (sin extensión): ") + ".csv"
        df.to_csv(file_name, index=False)
        print(f"El archivo '{file_name}' se ha guardado correctamente.")
        break
    elif opcion == "2":
        print(df.to_string(index=True))  # Mostrar todos los registros con índice
    elif opcion == "3":
        print("Saliendo sin guardar.")
        break
    else:
        print("Opción no válida. Intente nuevamente.")
