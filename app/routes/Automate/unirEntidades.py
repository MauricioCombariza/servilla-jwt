import os
import pandas as pd

def combinar_archivos(directorio_rel):
    """
    Combina todos los archivos .xls y .xlsx en un directorio y guarda el resultado en un nuevo archivo Excel.

    Parámetros:
    - directorio_rel: Ruta relativa al directorio que contiene los archivos .xls y .xlsx.

    Retorna:
    - None
    """
    # Asegúrate de que la carpeta "entidades" exista
    os.makedirs("app/routes/Automate/entidades", exist_ok=True)
    os.makedirs("app/routes/Automate/archivos", exist_ok=True)
    directorio_abs = os.path.join("app/routes/Automate/entidades")
    directorio_archivos = os.path.join("app/routes/Automate/archivos")
    # Obtener la ruta absoluta del directorio
    # directorio_abs = os.path.abspath(directorio_rel)

    # Verificar si el directorio existe
    if not os.path.exists(directorio_abs):
        print(f"El directorio '{directorio_abs}' no existe.")
        return

    # Lista para almacenar los DataFrames de los archivos .xls o .xlsx
    dataframes = []

    # Recorre todos los archivos en el directorio con extensiones .xls y .xlsx
    for archivo in os.listdir(directorio_abs):
        if archivo.endswith('.xls') or archivo.endswith('.xlsx'):
            # Lee cada archivo y almacena su contenido en un DataFrame
            ruta_completa = os.path.join(directorio_abs, archivo)
            df = pd.read_excel(ruta_completa)
            # Añade el DataFrame a la lista
            dataframes.append(df)
            
    # Combinar todos los DataFrames en uno solo
    resultado_final = pd.concat(dataframes, ignore_index=True)
        
    # Asegurarse de que el resultado final tenga solo dos columnas "ID" y "CUPONES"
    resultado_final = resultado_final[['ID', 'CUPONES']]
    # print(resultado_final)

    resultado_final.rename(columns={'CUPONES': 'DATO_ENTIDAD'}, inplace=True)
    
    ruta_final = os.path.join(directorio_archivos, 'bancos.xlsx')
    # Guardar el resultado en un nuevo archivo Excel
    resultado_final.to_excel(ruta_final, index=False)

    return print("Se unieron las entidades de forma exitosa!!")

# combinar_archivos('/entidades/')
