import os
import pandas as pd
import numpy as np
from openpyxl import load_workbook
import glob
from datetime import datetime

def generacion_robot(archivo_consolidado, archivo_contratos, archivo_robot, directorio):
    """
    Cálcula si las facturas pueden cancelarse, toma los datos de robot.xlsx y 
    le resta lo del total de cada uno y si es viable, genera el documento.
    Parámetros:
    - archivo_base_rel: Ruta relativa del archivo base.
    - directorio_rel: Ruta relativa al directorio que contiene los archivos .xls y .xlsx.
    - robot: Nombre del archivo Excel de salida. que es el que se incerta después en el robot.

    Retorna:
    - None
    """

    fecha = datetime.now().strftime("%d%m%Y")
    # Obtiene la ruta completa del archivo base
    ruta_completa_base_consolidado = os.path.join(os.getcwd(), archivo_consolidado)
    ruta_completa_base_contratos = os.path.join(os.getcwd(), archivo_contratos)

    # Verifica si el archivo contratos existe
    if not os.path.exists(ruta_completa_base_consolidado):
        print(f"El archivo base '{ruta_completa_base_consolidado}' no existe.")
        return

    # Lee el archivo base
    df_contratos = pd.read_excel(ruta_completa_base_contratos)
    # print(df_contratos)
    df_consolidado = pd.read_excel(ruta_completa_base_consolidado)
    df_filtrado = df_consolidado[df_consolidado['DATO_ENTIDAD'] != 0]
    df_filtrado = df_filtrado.reset_index(drop=True)
    # Realiza el join por el campo 'ID'
    df_resultado = pd.merge(df_filtrado, df_contratos, on='ID', how='left')
    # print(df_resultado.columns)
    df_resultado['V_TOTAL_UNE'] = np.where(df_resultado[10] > df_resultado['TOTAL_UNE'], df_resultado['TOTAL_UNE'], 0)
    df_resultado['V_TOTAL_EDATEL'] = np.where(df_resultado[20] > df_resultado['TOTAL_EDATEL'], df_resultado['TOTAL_EDATEL'], 0)
    df_resultado['V_TOTAL_TIGO'] = np.where(df_resultado[30] > df_resultado['TOTAL_TIGO'], df_resultado['TOTAL_TIGO'], 0)
    # print(df_resultado.columns)
#     df_resultado.rename(columns={'PEDIDO_x': 'PEDIDO'}, inplace=True)
#     # print(list(df_resultado.columns))

    df_intermedio = df_resultado[['ID', 'NOMBRE','PEDIDO', 'V_TOTAL_UNE', 'V_TOTAL_EDATEL', 'V_TOTAL_TIGO']]
    for i in range(len(df_intermedio)):
        workbook = load_workbook(archivo_robot)
        sheet_name = 'ea'
        sheet = workbook[sheet_name]
        # Coloca la información en las celdas especificadas
        sheet['B5'] = df_intermedio['PEDIDO'][i]
        sheet['B6'] = df_intermedio['PEDIDO'][i]
        sheet['B7'] = df_intermedio['PEDIDO'][i]
        nombre_une = f"Recau {df_intermedio['NOMBRE'][i]}"
        sheet['D5'] = nombre_une
        nombre_edatel = f"{df_intermedio['NOMBRE'][i]}-EDATEL"
        sheet['D6'] = nombre_edatel
        nombre_tigo = f"{df_intermedio['NOMBRE'][i]}-TIGO"
        sheet['D7'] = nombre_tigo
        valor_une = round(float(df_intermedio['V_TOTAL_UNE'][i]))
        sheet['F5'] = int(valor_une)
        valor_edatel = round(float(df_intermedio['V_TOTAL_EDATEL'][i]))
        sheet['F6'] = int(valor_edatel)
        valor_tigo = round(float(df_intermedio['V_TOTAL_TIGO'][i]))
        sheet['F7'] = int(valor_tigo)
        
        # Guarda los cambios en el archivo Excel
        nombre = f"{directorio}/{fecha}-{df_intermedio['PEDIDO'][i]}.xlsx" 
        workbook.save(nombre)
        workbook.close()
    

    # Especifica el directorio donde se encuentran los archivos .xlsx
    # directorio = 'robot/'

    # Busca todos los archivos con extensión .xlsx en el directorio
    archivos_xlsx = glob.glob(f'{directorio}/*.xlsx')

    # Lista para almacenar los DataFrames de cada archivo
    dataframes = []

    # Lee cada archivo y lo agrega al DataFrame
    for archivo in archivos_xlsx:
        df = pd.read_excel(archivo)
        dataframes.append(df)

    # Concatena los DataFrames en uno solo
    df_concatenado = pd.concat(dataframes, ignore_index=True)

    # Guarda el DataFrame concatenado en un nuevo archivo llamado resume.xlsx
    df_concatenado.to_excel(f'{directorio}/resume.xlsx', index=False)

print("El Robot se ha generado de forma exitosa !!")

