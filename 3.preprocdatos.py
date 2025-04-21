import pandas as pd
import re
import sys
from datetime import datetime
import os

# Verificar si se pasó un archivo como argumento
if len(sys.argv) < 2:
    print("Uso: python3 script.py <archivo_csv>")
    sys.exit(1)

file_path = sys.argv[1]

# Detectar separador del CSV
with open(file_path, "r", encoding="utf-8") as f:
    first_line = f.readline()
    sep = "," if "," in first_line else ";"

# Definir el orden y las columnas necesarias
columnas_requeridas = ['timestamp', 'origen_IP', 'destino_IP', 'hash_archivo', 'dominio', 'evento', 'descripcion', 'File', 'MD5']

# Cargar el dataset
df = pd.read_csv(file_path, encoding="utf-8", sep=sep, dtype=str, na_values="")

# Filtrar solo las columnas necesarias y en el orden correcto
columnas_presentes = [col for col in columnas_requeridas if col in df.columns]
df = df[columnas_presentes]

# Verificar si quedan columnas válidas
if df.empty or df.shape[1] == 0:
    print("El archivo CSV no contiene ninguna de las columnas requeridas. No se puede ejecutar el script.")
    sys.exit(1)

# Verificar valores nulos
print("Valores nulos en cada columna:")
print(df.isnull().sum())

# Copia del dataframe original para comparar después
df_original = df.copy()

# Listas para almacenar filas eliminadas
eliminadas = []

# Eliminar filas con valores nulos
df.dropna(inplace=True)

# Rellenar valores nulos en 'hash_archivo'
if 'hash_archivo' in df.columns:
    df['hash_archivo'] = df['hash_archivo'].fillna("SIN_HASH")

# Funciones de validación
def validar_ip(ip):
    if pd.isna(ip):
        return False
    patron_ip = r"^(25[0-5]|2[0-4][0-9]|1?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|1?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|1?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|1?[0-9][0-9]?)$"
    return bool(re.match(patron_ip, ip))

def validar_dominio(dominio):
    if pd.isna(dominio):
        return False
    patron_dominio = r"^(www\.)?[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*\.[a-zA-Z]{2,}$"
    return bool(re.match(patron_dominio, dominio))

def validar_timestamp(timestamp):
    if pd.isna(timestamp):
        return False
    formatos_validos = ["%d/%m/%Y %H:%M", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%d/%m/%Y %H:%M:%S", "%d-%m-%Y %H:%M:%S"]
    for formato in formatos_validos:
        try:
            datetime.strptime(timestamp, formato)
            return True
        except ValueError:
            continue
    return False

def validar_file(file):
    if pd.isna(file):
        return False
    patron_file = r"^.+\.[a-zA-Z0-9]{1,5}$"
    return bool(re.match(patron_file, file))

def validar_md5(md5):
    if pd.isna(md5):
        return False
    patron_md5 = r"^[a-fA-F0-9]{32}$"
    return bool(re.match(patron_md5, md5))

# Filtrar y registrar filas eliminadas
for index, row in df.iterrows():
    if ('origen_IP' in df.columns and not validar_ip(row['origen_IP'])) or \
       ('destino_IP' in df.columns and not validar_ip(row['destino_IP'])) or \
       ('dominio' in df.columns and not validar_dominio(row['dominio'])) or \
       ('timestamp' in df.columns and not validar_timestamp(row['timestamp'])) or \
       ('File' in df.columns and not validar_file(row['File'])) or \
       ('MD5' in df.columns and not validar_md5(row['MD5'])):
        eliminadas.append(row.values.tolist())
        df.drop(index, inplace=True)

# Verificar si hubo cambios en los datos
if df.equals(df_original):
    print("Los datos ya están normalizados. No hay cambios que guardar.")
    sys.exit(0)

# Mostrar las primeras filas después de la normalización
print("Datos normalizados:")
print(df.head())

# Informar sobre las líneas eliminadas
if eliminadas:
    print("\nLíneas eliminadas:")
    for linea in eliminadas:
        print(linea)

# Preguntar qué hacer con los resultados
print("\n¿Qué quieres hacer con estos resultados?")
print("1. Sobrescribir el actual dataset con estos cambios")
print("2. Generar un nuevo dataset con estos cambios")
print("3. No guardar cambios")
choice = input("Seleccione una opción (1/2/3): ")

# Guardar con separador ';' si el original usaba ','
new_sep = ";" if sep == "," else sep

if choice == '1':
    df.to_csv(file_path, encoding="utf-8", sep=new_sep, index=False)
    print(f"El archivo {file_path} ha sido sobrescrito con los nuevos cambios.")

elif choice == '2':
    new_file_name = input("Ingrese el nombre del nuevo archivo (sin extensión): ")
    new_file_path = f"{new_file_name}.csv"
    
    if os.path.exists(new_file_path):
        overwrite = input(f"El archivo {new_file_path} ya existe. ¿Deseas sobrescribirlo? [S/n]: ")
        if overwrite.lower() != 's':
            print("Operación cancelada.")
            sys.exit(0)
    
    df.to_csv(new_file_path, encoding="utf-8", sep=new_sep, index=False)
    print(f"El nuevo dataset se ha guardado como {new_file_path}.")

elif choice == '3':
    print("No se han guardado cambios.")
    sys.exit(0)

else:
    print("Opción no válida. No se han guardado cambios.")
