import pandas as pd
import os
import sys

# Verificar si se ha pasado el archivo como argumento
if len(sys.argv) < 2:
    print("Uso: python script.py <archivo_csv>")
    exit()

archivo_csv = sys.argv[1]
if not os.path.isfile(archivo_csv):
    print(f"El archivo '{archivo_csv}' no existe.")
    exit()

print(f"Archivo seleccionado: {archivo_csv}")

# Cargar el archivo CSV con separador ';'
df = pd.read_csv(archivo_csv, encoding='utf-8', sep=';')

# Convertir la columna 'timestamp' a formato datetime, manejando múltiples formatos
def convertir_fecha(fecha):
    formatos = ['%d/%m/%Y %H:%M', '%Y-%m-%d %H:%M:%S']
    for formato in formatos:
        try:
            return pd.to_datetime(fecha, format=formato)
        except ValueError:
            continue
    return pd.NaT  # Devuelve NaT si no coincide con ningún formato

df['timestamp'] = df['timestamp'].apply(convertir_fecha)

# Lista de eventos considerados de alto riesgo
eventos_riesgo = ['Acceso no autorizado', 'Autenticación fallida', 'Transferencia de datos']

# Identificar registros con eventos de alto riesgo
df['evento_riesgo'] = df['evento'].apply(lambda ev: ev in eventos_riesgo)

# Análisis por horario
def fuera_de_horario(ts):
    # Consideramos fuera del horario laboral aquellos registros entre 00:00 y 06:00
    if pd.notna(ts):
        return ts.hour >= 0 and ts.hour < 6
    return False

df['fuera_horario'] = df['timestamp'].apply(fuera_de_horario)

# Mostrar resumen de cambios realizados
print("\nResumen de cambios realizados:")
print(df.head())

# Menú para guardar el archivo
while True:
    print("\nOpciones de guardado:")
    print("1. Sobrescribir el actual archivo con la nueva información")
    print("2. Guardar los datos en un archivo nuevo")
    print("3. Ver todos los cambios en el documento")
    print("4. No guardar los datos")
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
        print("\nCambios realizados en el documento:")
        print(df[df.columns.difference(['timestamp'])].to_string(index=False))
    elif opcion == "4":
        print("Operación cancelada. No se guardó ningún archivo.")
        break
    else:
        print("Opción no válida. Intente de nuevo.")
