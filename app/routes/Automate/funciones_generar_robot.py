from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from pathlib import Path
from zipfile import ZipFile
import os
import pandas as pd
import numpy as np
from openpyxl import load_workbook
import glob
from datetime import datetime
from io import BytesIO


def create_robot_files():
    try:
        # Rutas a los archivos necesarios
        script_directory = Path(__file__).parent
        consolidado_path = script_directory / "archivos/consolidadoFinal.xlsx"
        contratos_path = script_directory / "archivos/contratos.xlsx"
        robot_template_path = script_directory / "archivos/base/robot.xlsx"

        # Genera los archivos robot en bits
        buffer = generate_robot_files(consolidado_path, contratos_path, robot_template_path)

        # Especifica el nombre del archivo zip que se va a descargar
        zip_filename = "robot_files.zip"

        # Configura el encabezado para la descarga del archivo zip
        content_disposition = f"attachment;filename={zip_filename}"

        # Devuelve una StreamingResponse directamente desde el contenido del archivo zip
        return StreamingResponse(
            iter(lambda: buffer.read(4096), b""),  # Lee el archivo en bloques de 4 KB
            media_type="application/zip",
            headers={"Content-Disposition": content_disposition},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar el archivo zip: {str(e)}")

def generate_robot_files(consolidado_path, contratos_path, robot_template_path):
    fecha = datetime.now().strftime("%d%m%Y")

    # Lee los archivos base
    df_contratos = pd.read_excel(contratos_path)
    df_consolidado = pd.read_excel(consolidado_path)

    # Filtra y realiza el join por el campo 'ID'
    df_filtrado = df_consolidado[df_consolidado['DATO_ENTIDAD'] != 0]
    df_resultado = pd.merge(df_filtrado, df_contratos, on='ID', how='left')

    # Inicializa un buffer de bytes para el archivo zip
    buffer = BytesIO()

    with ZipFile(buffer, 'w') as zip_file:
        for i, row in df_resultado.iterrows():
            # Crea un DataFrame intermedio para cada fila
            df_intermedio = pd.DataFrame({
                'ID': [row['ID']],
                'NOMBRE': [row['NOMBRE']],
                'PEDIDO': [row['PEDIDO']],
                'V_TOTAL_UNE': [min(row[10], row['TOTAL_UNE'])],
                'V_TOTAL_EDATEL': [min(row[20], row['TOTAL_EDATEL'])],
                'V_TOTAL_TIGO': [min(row[30], row['TOTAL_TIGO'])],
            })

            # Genera el archivo robot en bits
            robot_content = generate_single_robot_file(df_intermedio, robot_template_path)

            # Añade el archivo robot al archivo zip
            zip_file.writestr(f"{fecha}-{row['PEDIDO']}.xlsx", robot_content)

    # Coloca el puntero del buffer al principio para permitir la lectura
    buffer.seek(0)
    return buffer

def generate_single_robot_file(df_intermedio, robot_template_path):
    # Abre el archivo robot en modo lectura
    with open(robot_template_path, 'rb') as robot_template:
        # Carga el contenido del archivo robot
        robot_content = robot_template.read()

        # Carga el archivo robot en un DataFrame de Pandas
        df_robot = pd.read_excel(BytesIO(robot_content))

        # Actualiza el contenido del archivo robot con los datos de df_intermedio
        df_robot['PEDIDO'] = df_intermedio['PEDIDO']
        df_robot['DATO_ENTIDAD'] = df_intermedio['NOMBRE']
        df_robot['TOTAL_UNE'] = df_intermedio['V_TOTAL_UNE']
        df_robot['TOTAL_EDATEL'] = df_intermedio['V_TOTAL_EDATEL']
        df_robot['TOTAL_TIGO'] = df_intermedio['V_TOTAL_TIGO']

        # Guarda el DataFrame actualizado en un BytesIO
        updated_robot_content = BytesIO()
        with pd.ExcelWriter(updated_robot_content, engine='openpyxl', mode='w') as writer:
            df_robot.to_excel(writer, index=False)

        # Coloca el puntero del buffer al principio para permitir la lectura
        updated_robot_content.seek(0)

        return updated_robot_content

print("El Robot se ha generado de forma exitosa !!")
