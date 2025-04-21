import pandas as pd
import os
import sys

# Asegurarse de que se pase un argumento con el archivo CSV
if len(sys.argv) < 2:
    print("Por favor, pase el nombre del archivo CSV como argumento.")
    sys.exit(1)

nombre_archivo = sys.argv[1]

# Verificar si el archivo existe
if not os.path.isfile(nombre_archivo):
    print(f"El archivo {nombre_archivo} no existe.")
    sys.exit(1)

# Cargar el archivo CSV con separador ';'
nombre_sin_extension = os.path.splitext(nombre_archivo)[0]
df = pd.read_csv(nombre_archivo, encoding='utf-8', sep=';')

# Intentar convertir 'timestamp' en ambos formatos
def convertir_timestamp(timestamp):
    try:
        # Primero intentamos el formato DD/MM/YYYY HH:MM
        return pd.to_datetime(timestamp, format='%d/%m/%Y %H:%M', errors='coerce')
    except ValueError:
        # Si falla, intentamos el formato ISO YYYY-MM-DD HH:MM:SS
        return pd.to_datetime(timestamp, format='%Y-%m-%d %H:%M:%S', errors='coerce')

# Aplicar la conversión a la columna 'timestamp'
df['timestamp'] = df['timestamp'].apply(convertir_timestamp)

# Definir eventos de riesgo
eventos_riesgo = ['Acceso no autorizado', 'Autenticación fallida', 'Transferencia de datos']

def analizar_registro(registro, index):
    es_evento_riesgoso = registro['evento'] in eventos_riesgo
    es_fuera_horario = 0 <= registro['timestamp'].hour < 6
    dominio_riesgoso = 'malware' in str(registro['dominio']).lower()
    hash_presente = pd.notna(registro['hash_archivo'])
    es_sospechoso = es_evento_riesgoso or es_fuera_horario or dominio_riesgoso
    
    resolucion = (
        f"\nResolución del Registro {index}:\n"
        f"Evento: {registro['evento']} - {'RIESGOSO' if es_evento_riesgoso else 'Normal'}\n"
        f"Horario: {registro['timestamp']} - {'Fuera de horario laboral' if es_fuera_horario else 'Horario normal'}\n"
        f"Dominio: {registro['dominio']} - {'RIESGOSO' if dominio_riesgoso else 'Normal'}\n"
        f"Hash presente: {registro['hash_archivo']} - {'Presente' if hash_presente else 'No disponible'}\n"
        f"Clasificación general: {'Sospechoso' if es_sospechoso else 'No sospechoso'}\n"
    )
    
    return resolucion

# Mostrar la primera resolución antes del menú
if not df.empty:
    print("Primer registro analizado:")
    print(analizar_registro(df.iloc[0], 1))
else:
    print("No hay registros en el archivo.")

# Menú de opciones
while True:
    print("\nOpciones:")
    print("1. Escribir las resoluciones en un documento")
    print("2. Mostrar las resoluciones en pantalla")
    print("3. No hacer nada")
    opcion = input("Seleccione una opción (1/2/3): ")

    if opcion == "1":
        nombre_salida = input("Ingrese el nombre del archivo para guardar las resoluciones: ")
        nombre_salida += ".txt"  # Asegurar que tenga la extensión .txt

        with open(nombre_salida, "w", encoding="utf-8") as file:
            file.write(f"Resolución del documento {nombre_sin_extension}.csv\n\n")
            for i, row in enumerate(df.itertuples(index=False), start=1):
                file.write(analizar_registro(row._asdict(), i))

        print(f"Resolución enviada al documento {nombre_salida}")
        break
    elif opcion == "2":
        print("\nResoluciones completas:")
        for i, row in enumerate(df.itertuples(index=False), start=1):
            print(analizar_registro(row._asdict(), i))
    elif opcion == "3":
        print("Operación cancelada. No se realizó ninguna acción.")
        break
    else:
        print("Opción no válida. Intente de nuevo.")
