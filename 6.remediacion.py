import pandas as pd
import os
import sys

# Comprobar si se pasó un archivo como argumento
if len(sys.argv) != 2:
    print("Por favor, pase un archivo CSV como argumento.")
    sys.exit(1)

# Definir la ruta del archivo CSV desde los argumentos
archivo_csv = sys.argv[1]

# Cargar el archivo CSV con separador ';'
df = pd.read_csv(archivo_csv, encoding='utf-8', sep=';')

# Convertir timestamp a formato datetime sin un formato fijo (permitir inferencia)
df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce', dayfirst=False)

# Identificar IPs externas
df['ip_externa'] = ~df['origen_IP'].str.startswith(('192.', '10.', '172.16.', '172.31.'))

# Identificar dominios sospechosos
df['dominio_sospechoso'] = df['dominio'].str.contains('suspicious', case=False, na=False)

# Lista de eventos considerados de alto riesgo
eventos_riesgo = ['Acceso no autorizado', 'Autenticación fallida', 'Transferencia de datos']
df['evento_riesgo'] = df['evento'].apply(lambda ev: ev in eventos_riesgo)

# Identificar accesos fuera del horario laboral
def fuera_de_horario(ts):
    return ts.hour >= 0 and ts.hour < 6
df['fuera_horario'] = df['timestamp'].apply(fuera_de_horario)

# Consolidar indicadores de compromiso
df['indicador'] = df[['ip_externa', 'dominio_sospechoso', 'evento_riesgo', 'fuera_horario']].any(axis=1)

# Aplicar medidas de remediación
def aplicar_medidas(row):
    acciones = []
    if row['ip_externa']:
        acciones.append("Bloquear IP en firewall")
    if row['dominio_sospechoso']:
        acciones.append("Añadir dominio a lista negra")
    if row['evento_riesgo']:
        acciones.append("Revisar políticas de acceso y autenticación")
    if row['fuera_horario']:
        acciones.append("Generar alerta por acceso fuera de horario")
    if pd.notna(row['hash_archivo']): 
        acciones.append("Actualizar firmas y añadir hash a lista negra de antivirus")
    return ", ".join(acciones)

df['medidas_remediacion'] = df.apply(aplicar_medidas, axis=1)

# Menú de opciones
while True:
    print("\nOpciones:")
    print("1. Sobrescribir el archivo original con las remediaciones")
    print("2. Escribir las remediaciones en un archivo nuevo")
    print("3. Mostrar las remediaciones")
    print("4. No hacer nada")
    opcion = input("Seleccione una opción (1/2/3/4): ")

    if opcion == "1":
        # Sobrescribir el archivo original
        df.to_csv(archivo_csv, sep=';', index=False)
        print(f"El archivo original ha sido sobrescrito: {archivo_csv}")
        break
    elif opcion == "2":
        # Guardar en un archivo nuevo
        nombre_salida = input("Ingrese el nombre del archivo para guardar las remediaciones (se guardará como .csv): ")
        nombre_salida = f"{nombre_salida}.csv"
        if os.path.exists(nombre_salida):
            sobrescribir = input("El archivo ya existe. ¿Desea sobrescribirlo? (s/n): ")
            if sobrescribir.lower() != 's':
                continue
        df.to_csv(nombre_salida, sep=';', index=False)
        print(f"Archivo guardado como: {nombre_salida}")
        break
    elif opcion == "3":
        # Mostrar las remediaciones
        print("\nRemediaciones aplicadas:")
        print(df[['timestamp', 'origen_IP', 'evento', 'medidas_remediacion']])
    elif opcion == "4":
        print("Operación cancelada. No se realizó ninguna acción.")
        break
    else:
        print("Opción no válida. Intente de nuevo.")
