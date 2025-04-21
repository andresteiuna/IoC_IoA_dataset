#!/bin/bash

while true; do
    clear
    echo "====================================="
    echo "          MENU PRINCIPAL            "
    echo "====================================="
    echo "1- Generar un Dataset"
    echo "2- Preparación y carga de datos"
    echo "3- Procesamiento de datos"
    echo "4- Identificar IOC"
    echo "5- Identificar IOA"
    echo "6- Remediación"
    echo "7- Resolución 3"
    echo "8- Machine Learning"
    echo "9- Salir"
    echo "====================================="
    read -p "Seleccione una opción: " opcion
    
    case $opcion in
        1) python3 1.generardataset.py; read -p "Presione Enter para continuar..." ;;
        2 | 3 | 4 | 5 | 6 | 7 | 8) 
            echo "Archivos CSV disponibles:" 
            csv_files=(*.csv)
            for i in "${!csv_files[@]}"; do
                echo "$((i+1))) ${csv_files[i]}"
            done
            read -p "Seleccione un archivo CSV por número: " csv_choice
            if [[ $csv_choice -gt 0 && $csv_choice -le ${#csv_files[@]} ]]; then
                selected_csv="${csv_files[$((csv_choice-1))]}"
                case $opcion in
                    2) script_name="2.pandas_backup.py" ;;
                    3) script_name="3.preprocdatos.py" ;;
                    4) script_name="4.identificarIOC.py" ;;
                    5) script_name="5.identificarIOA.py" ;;
                    6) script_name="6.remediacion.py" ;;
                    7) script_name="7.resolucion.py" ;;
                    8) script_name="8.machinelearning.py" ;;
                esac
                echo "Ejecutando $script_name con $selected_csv..."
                python3 "$script_name" "$selected_csv"
            else
                echo "Selección no válida."
            fi
            read -p "Presione Enter para continuar..." 
            ;;
        9) echo "Saliendo..."; exit 0 ;;
        *) echo "Opción no válida, intente nuevamente"; sleep 2 ;;
    esac

done
