import pandas as pd
import sys

# Verificar si se pasó un archivo como argumento
if len(sys.argv) < 2:
    print("Uso: python3 pandas_backup.py <archivo_csv>")
    sys.exit(1)

file_path = sys.argv[1]  # Obtener el archivo CSV desde los argumentos

try:
    # Cargar el dataset con detección automática del delimitador
    df = pd.read_csv(file_path, encoding="ISO-8859-1", sep=None, engine='python', na_values="")
    
    # Mostrar las primeras filas para verificar que se cargó correctamente
    print("Primeras filas del archivo seleccionado:")
    print(df.head())
    
    # Verificar si la columna 'timestamp' existe antes de convertirla
    timestamp_col = 'timestamp'
    if timestamp_col in df.columns:
        df[timestamp_col] = pd.to_datetime(df[timestamp_col], format='%d/%m/%Y %H:%M', errors='coerce', dayfirst=True)
    
    # Reconvertir la codificación de texto si hay caracteres mal formateados
    def convert_encoding(series):
        if series.dtype == "object":
            return series.str.encode('ISO-8859-1', errors='ignore').str.decode('utf-8', errors='ignore')
        return series

    df = df.apply(convert_encoding)

    # Mostrar todas las columnas y filas cargadas correctamente
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', 10)  # Limitar la cantidad de filas mostradas
    print("\nDatos procesados:")
    print(df)
    
    # Menú de opciones
    while True:
        print("\nMenú:")
        print("1. Mostrar todas las líneas del documento")
        print("2. Salir")
        
        opcion = input("Seleccione una opción: ")
        
        if opcion == "1":
            print(df.to_string(index=False))
        elif opcion == "2":
            print("Saliendo...")
            break
        else:
            print("Opción no válida. Intente nuevamente.")
except Exception as e:
    print(f"Error al procesar el archivo: {e}")
