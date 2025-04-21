import pandas as pd
import re
import os
import sys

# Verificar si se ha pasado el archivo como argumento
if len(sys.argv) < 2:
    print("Uso: python 4.identificarIOC.py <archivo_csv>")
    exit()

archivo_csv = sys.argv[1]
if not os.path.isfile(archivo_csv):
    print(f"El archivo '{archivo_csv}' no existe.")
    exit()

print(f"Archivo seleccionado: {archivo_csv}")

# Función para detectar el delimitador (coma o punto y coma)
def detectar_delimitador(ruta):
    with open(ruta, "r", encoding="utf-8") as f:
        line = f.readline()
        if ";" in line:
            return ";"
        elif "," in line:
            return ","
        else:
            raise ValueError("No se pudo detectar el delimitador adecuado en el archivo.")

# Cargar el dataset asegurando el formato de fecha y el delimitador
def cargar_datos(ruta):
    try:
        delimitador = detectar_delimitador(ruta)
        df = pd.read_csv(ruta, sep=delimitador, parse_dates=['timestamp'], dayfirst=True)
        return df
    except Exception as e:
        print(f"Error al leer el archivo CSV: {e}")
        sys.exit(1)

# Cargar los datos
df = cargar_datos(archivo_csv)

# Función para identificar si una IP es privada
def es_ip_privada(ip):
    try:
        ip_partes = list(map(int, ip.split('.')))
        if ip_partes[0] == 10:
            return True
        if ip_partes[0] == 172 and 16 <= ip_partes[1] <= 31:
            return True
        if ip_partes[0] == 192 and ip_partes[1] == 168:
            return True
    except:
        return False
    return False

# Identificar direcciones IP externas (potencialmente maliciosas) en el campo 'origen_IP'
df['ip_externa'] = df['origen_IP'].apply(lambda ip: not es_ip_privada(ip))

# Función para identificar el tipo de hash
def tipo_hash(hash_value):
    if pd.isna(hash_value) or hash_value.strip() == "":
        return None
    hash_value = hash_value.strip()
    if re.fullmatch(r"[a-fA-F0-9]{32}", hash_value):
        return "MD5"
    elif re.fullmatch(r"[a-fA-F0-9]{64}", hash_value):
        return "SHA256"
    else:
        return "Desconocido"

# Identificar el tipo de hash en la columna 'hash_archivo'
df['tipo_hash'] = df['hash_archivo'].apply(tipo_hash)

# Función para identificar dominios sospechosos
def es_dominio_sospechoso(dominio):
    palabras_clave = ['malware', 'suspicious']
    dominio = str(dominio).lower()
    return any(palabra in dominio for palabra in palabras_clave)

# Identificar dominios sospechosos en la columna 'dominio'
df['dominio_sospechoso'] = df['dominio'].apply(es_dominio_sospechoso)

# Mostrar resumen de cambios realizados
print("\nResumen de cambios realizados:")
print(df.head())

# Menú para guardar el archivo
while True:
    print("\nOpciones de guardado:")
    print("1. Sobrescribir el actual archivo con la nueva información")
    print("2. Guardar los datos en un archivo nuevo")
    print("3. No guardar los datos")
    print("4. Ver todos los cambios en el documento")
    opcion = input("Seleccione una opción (1/2/3/4): ")
    
    if opcion == "1":
        df.to_csv(archivo_csv, sep=';', index=False)
        print(f"Archivo sobrescrito: {archivo_csv}")
        break
    elif opcion == "2":
        nombre_salida = input("Ingrese el nombre del archivo de salida (sin extensión): ") + ".csv"
        if os.path.exists(nombre_salida):
            confirmacion = input(f"El archivo '{nombre_salida}' ya existe. ¿Desea sobrescribirlo? (S/n): ").strip().lower()
            if confirmacion != 's':
                continue
        df.to_csv(nombre_salida, sep=';', index=False)
        print(f"Archivo guardado como: {nombre_salida}")
        break
    elif opcion == "3":
        print("Operación cancelada. No se guardó ningún archivo.")
        break
    elif opcion == "4":
        print("\nCambios realizados en el documento:")
        print(df.to_string())
    else:
        print("Opción no válida. Intente de nuevo.")
