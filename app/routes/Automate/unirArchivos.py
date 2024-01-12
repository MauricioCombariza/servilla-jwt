import os
import pandas as pd
import numpy as np

def procesar_archivos(archivo_base_rel, directorio_rel, resultado_excel='unionArchivos.xlsx', excluir='contratos.xlsx'):
    """
    Combina los datos de un archivo base con varios archivos en un directorio y realiza operaciones.

    Parámetros:
    - archivo_base_rel: Ruta relativa del archivo base.
    - directorio_rel: Ruta relativa al directorio que contiene los archivos .xls y .xlsx.
    - resultado_excel: Nombre del archivo Excel de salida. Por defecto, se llama 'test.xlsx'.

    Retorna:
    - None
    """
    # Obtiene la ruta completa del archivo base
    ruta_completa_base = os.path.join(os.getcwd(), archivo_base_rel)

    # Verifica si el archivo base existe
    if not os.path.exists(ruta_completa_base):
        print(f"El archivo base '{ruta_completa_base}' no existe.")
        return

    # Lee el archivo base
    df_base = pd.read_excel(ruta_completa_base)
    
    # Lista para almacenar los DataFrames de los archivos .xls o .xlsx
    dataframes = []

    # Recorre todos los archivos en el directorio con extensiones .xls y .xlsx
    for archivo in os.listdir(directorio_rel):
        if archivo != "contratos.xlsx":
            if archivo.endswith('.xls') or archivo.endswith('.xlsx'):
                # Lee cada archivo y almacena su contenido en un DataFrame
                ruta_completa = os.path.join(directorio_rel, archivo)
                df_temporal = pd.read_excel(ruta_completa)
                # print(df_temporal)

                # Añade el DataFrame a la lista
                dataframes.append(df_temporal)

    # Realiza un join en la columna 'ID'
    df_resultado = df_base.copy()

    for df_temporal in dataframes:
        # Fusionar y eliminar columnas duplicadas con sufijos diferentes
        df_resultado = pd.merge(df_resultado, df_temporal, on='ID', how='left', suffixes=('', '_temporal'))

    df_resultado.fillna(0, inplace=True)
    df_resultado['UNE'] = np.where(df_resultado['CUPONES'] < df_resultado['DATO_ENTIDAD'],
                                   df_resultado['CUPONES'] - (df_resultado['TIGO'] + df_resultado['EDATEL']),
                                   df_resultado['DATO_ENTIDAD'] - (df_resultado['TIGO'] + df_resultado['EDATEL']))
    # Reordenar las columnas colocando 'CUPONES' al final
    columnas_ordenadas = [col for col in df_resultado.columns if col != 'CUPONES'] + ['CUPONES']
    df_resultado = df_resultado[columnas_ordenadas]
    # Reordenar las columnas colocando 'DATO_ENTIDAD' al final
    columnas_ordenadas = [col for col in df_resultado.columns if col != 'DATO_ENTIDAD'] + ['DATO_ENTIDAD']
    df_resultado = df_resultado[columnas_ordenadas]
    # Eliminar columnas temporales
    columnas_a_eliminar = [col for col in df_resultado.columns if isinstance(col, str) and col.endswith('_temporal')]

    # columnas_a_eliminar = [col for col in df_resultado.columns if col.endswith('_temporal')]
    df_resultado.drop(columns=columnas_a_eliminar, inplace=True)
    df_resultado['DIFERENCIA'] = df_resultado['CUPONES'] - df_resultado['DATO_ENTIDAD']

    # Imprime el resultado
    print("Resultado exitoso")
    df_resultado.to_excel(resultado_excel)
    return df_resultado

# Ejemplo de uso:
# Supongamos que tienes un archivo base 'base.xlsx' y un directorio 'archivos/'
# procesar_archivos('archivos/base.xlsx', 'archivos/')
