import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import IsolationForest
import numpy as np
import sys
import os
import matplotlib.pyplot as plt
import seaborn as sns

# Detectar el delimitador del archivo
def detectar_delimitador(ruta):
    with open(ruta, "r", encoding="utf-8") as f:
        line = f.readline()
        if ";" in line:
            return ";"
        elif "," in line:
            return ","
        else:
            raise ValueError("No se pudo detectar el delimitador adecuado en el archivo.")

# Cargar el dataset con el delimitador correcto
def cargar_datos(ruta):
    try:
        delimitador = detectar_delimitador(ruta)
        df = pd.read_csv(ruta, delimiter=delimitador, on_bad_lines='skip', encoding='utf-8')
        return df
    except Exception as e:
        print(f"Error al leer el archivo CSV: {e}")
        sys.exit(1)

# Preprocesar los datos
def preprocesar_datos(df):
    df.fillna("desconocido", inplace=True)
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors='coerce')
    df["hora"] = df["timestamp"].dt.hour
    df["dia_semana"] = df["timestamp"].dt.weekday
    df["semana_mes"] = ((df["timestamp"].dt.day - 1) // 7) + 1
    df["mes"] = df["timestamp"].dt.month
    df["año"] = df["timestamp"].dt.year
    
    encoder = LabelEncoder()
    for col in ["origen_IP", "destino_IP", "hash_archivo", "dominio", "evento"]:
        df[col] = encoder.fit_transform(df[col])
    
    features = ["origen_IP", "destino_IP", "hash_archivo", "dominio", "hora", "dia_semana"]
    X = df[features]
    return X, df

# Entrenar modelo de detección de anomalías
def entrenar_modelo(X, df):
    modelo = IsolationForest(contamination=0.1, random_state=42)
    modelo.fit(X)
    df["anomaly_score"] = modelo.decision_function(X)
    df["anomaly"] = modelo.predict(X)
    return df

# Visualizar las anomalías para todas las semanas juntas y guardarlo en un solo gráfico
def visualizar_anomalias_todas_semanas(df):
    plt.figure(figsize=(10, 6))

    # Ordenamos por hora y día de la semana
    df_ordenado = df.sort_values(by=["hora", "dia_semana"])

    # Crear una lista para almacenar los puntos que se dibujarán, según las prioridades de los colores
    puntos_a_dibujar = []

    for _, row in df_ordenado.iterrows():
        hora = row["hora"]
        dia_semana = row["dia_semana"]
        anomaly = row["anomaly"]
        
        if anomaly == 1:
            color = 'green'  # Anomalía normal
        elif anomaly == -1 and row["anomaly_score"] > 0:
            color = 'orange'  # Anomalía naranja
        else:
            color = 'red'  # Anomalía roja

        puntos_a_dibujar.append((hora, dia_semana, color))

    # Dibujar los puntos
    for hora, dia_semana, color in puntos_a_dibujar:
        plt.scatter(hora, dia_semana, color=color, marker='o')

    plt.yticks(ticks=range(7), labels=["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"])
    plt.title("Detección de Anomalías - Todas las Semanas Combinadas")
    plt.xlabel("Hora")
    plt.ylabel("Día de la Semana")

    # Pedir al usuario que ingrese el nombre del archivo
    nombre_archivo = input("Ingrese el nombre del archivo para guardar el gráfico (sin extensión): ") + ".png"
    
    # Guardar el gráfico con el nombre dado por el usuario
    plt.savefig(nombre_archivo)
    print(f"Gráfico guardado como {nombre_archivo}")

# Visualizar anomalías para una semana específica
def visualizar_anomalias(df, semana_mes, mes, año, guardar=False):
    df_semana = df[(df["semana_mes"] == semana_mes) & (df["mes"] == mes) & (df["año"] == año)]
    
    plt.figure(figsize=(10, 6))

    # Ordenamos por hora y día de la semana
    df_ordenado = df_semana.sort_values(by=["hora", "dia_semana"])

    # Crear una lista para almacenar los puntos que se dibujarán, según las prioridades de los colores
    puntos_a_dibujar = []

    for _, row in df_ordenado.iterrows():
        hora = row["hora"]
        dia_semana = row["dia_semana"]
        anomaly = row["anomaly"]
        
        if anomaly == 1:
            color = 'green'  # Anomalía normal
        elif anomaly == -1 and row["anomaly_score"] > 0:
            color = 'orange'  # Anomalía naranja
        else:
            color = 'red'  # Anomalía roja

        puntos_a_dibujar.append((hora, dia_semana, color))

    # Dibujar los puntos
    for hora, dia_semana, color in puntos_a_dibujar:
        plt.scatter(hora, dia_semana, color=color, marker='o')

    plt.yticks(ticks=range(7), labels=["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"])
    plt.title(f"Detección de Anomalías - Semana {semana_mes} del mes {mes} del año {año}")
    plt.xlabel("Hora")
    plt.ylabel("Día de la Semana")

    # Guardar el gráfico si se ha indicado
    if guardar:
        nombre_archivo = f"grafico_semana_{semana_mes}_mes_{mes}_año_{año}.png"
        plt.savefig(nombre_archivo)
        print(f"Gráfico guardado como {nombre_archivo}")
    else:
        plt.show()

# Mostrar semanas detectadas y permitir al usuario elegir
def menu_opciones(df):
    semanas_detectadas = df[["semana_mes", "mes", "año"]].drop_duplicates().sort_values(by=["año", "mes", "semana_mes"])
    
    print("\nSe han detectado las siguientes semanas:")
    for i, row in semanas_detectadas.iterrows():
        print(f"Semana {row['semana_mes']} del mes {row['mes']} del año {row['año']}")
    
    print("\nSeleccione una opción:")
    print("1. Generar y guardar gráficos para todas las semanas")
    print("2. Elegir una semana específica para visualizar y guardar el gráfico")
    print("3. Guardar todas las semanas en un solo gráfico")
    print("4. No hacer nada")
    
    opcion = input("Ingrese el número de la opción: ")
    if opcion == "1":
        for i, row in semanas_detectadas.iterrows():
            visualizar_anomalias(df, row["semana_mes"], row["mes"], row["año"], guardar=True)
    elif opcion == "2":
        semana_mes = int(input("Ingrese el número de la semana del mes: "))
        mes = int(input("Ingrese el número del mes: "))
        año = int(input("Ingrese el año: "))
        visualizar_anomalias(df, semana_mes, mes, año, guardar=True)
    elif opcion == "3":
        visualizar_anomalias_todas_semanas(df)
    elif opcion == "4":
        print("Operación cancelada.")
    else:
        print("Opción no válida.")
    
    mostrar_y_guardar_csv(df)

# Mostrar las primeras 5 líneas y dar opción de ver todo el archivo
def mostrar_y_guardar_csv(df):
    while True:
        print("\nPrimeras 5 líneas del archivo (incluyendo la cabecera):")
        print(df.head(5).to_string(index=False))
        
        print("\nSeleccione una opción:")
        print("1. Sobreescribir el archivo actual")
        print("2. Guardar como un nuevo archivo")
        print("3. Ver el archivo completo")
        print("4. No guardar el archivo")
        
        opcion = input("Ingrese el número de la opción: ")
        if opcion == "1":
            df.to_csv(ruta_csv, index=False)
            print("Archivo sobrescrito con éxito.")
            break
        elif opcion == "2":
            nuevo_nombre = input("Ingrese el nombre del nuevo archivo (sin extensión): ")
            df.to_csv(f"{nuevo_nombre}.csv", index=False)
            print(f"Archivo guardado como {nuevo_nombre}.csv")
            break
        elif opcion == "3":
            print(df.to_string(index=False))
            continue  # Vuelve a mostrar el menú después de ver el archivo completo
        elif opcion == "4":
            print("El archivo no se ha guardado.")
            break
        else:
            print("Opción no válida.")

# Ejecutar todo el proceso
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python script.py <ruta_csv>")
        sys.exit(1)
    
    ruta_csv = sys.argv[1]
    df = cargar_datos(ruta_csv)
    X, df = preprocesar_datos(df)
    df_resultado = entrenar_modelo(X, df)
    menu_opciones(df_resultado)
