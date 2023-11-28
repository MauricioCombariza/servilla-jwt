# Python
import shutil
from io import BytesIO
import os
import re
import tempfile
import io

# Pydantic
# Fastapi
from fastapi.responses import StreamingResponse, FileResponse
from fastapi import APIRouter, Path, HTTPException, Form, File, UploadFile, Request, Query
from fastapi.params import Depends
from pydantic import BaseModel


# Terceros
from sqlalchemy.orm import Session
import pandas as pd
import numpy as np
from typing import List

# Modulos locales
from app.models.events import Historico
from app.database.connection import get_session, engine
from app.auth.jwt_bearer import jwtBearer, decodeJWT
from app.database.lists.lists import regex
from app.routes.documents.functions_gestioOrdenesCarvajal import load_dataframes, filter_dataframe, merge_and_fillna, apply_conditions, merge_motivos_and_finalize, get_current_date
from app.routes.documents.functions_gestion import filter_and_format_data, create_dataframe, filter_by_dates, assign_status_column, create_excel_response

class InputData(BaseModel):
    ordenInicio: int
    ordenFin: int


document_router = APIRouter(
    tags=["Documents"]
)

@document_router.post("/direcciones/")
def ajusteDireccion(file: UploadFile = File(...)):
    # archivo = "/mnt/c/Users/mcomb/OneDrive/Escritorio/Carvajal/python/original_direcciones.txt"
    global upload_folder
    upload_folder = '/mnt/c/Users/mcomb/OneDrive/Escritorio/Carvajal/python/direcciones'
    file_object = file.file
    #create empty file to copy the file_object to
    upload_folder = open(os.path.join(upload_folder, file.filename), 'wb+')
    shutil.copyfileobj(file_object, upload_folder)
    upload_folder.close()
    archivo = '/mnt/c/Users/mcomb/OneDrive/Escritorio/Carvajal/python/direcciones/{}'.format(file.filename)
    for i in range (0, len(regex)):
        with open(archivo, 'r', encoding='utf8', errors='ignore') as file:
            contenido = file.read()
            # Realizar el reemplazo con la función sub() de re
            contenido_nuevo = re.sub(regex[i]['patron'], regex[i]['reemplazo'], contenido)
            # Sobrescribir el archivo con el contenido nuevo
            with open(archivo, 'w') as file:
                file.write(contenido_nuevo)
    nombre_archivo_entrada = archivo
    nombre_archivo_salida = '/mnt/c/Users/mcomb/OneDrive/Escritorio/Carvajal/python/direcciones/direcciones_salida.txt'

    with open(nombre_archivo_entrada, 'r') as archivo_entrada, open(nombre_archivo_salida, 'w') as archivo_salida:
        for linea in archivo_entrada:
            linea_modificada = re.sub(r'^(\w{2})(\s?\s?\s?\s)?(\d\d?\d?)(\s?\s?\s?\s)?(BIS|Bis|bis)?(\s?\s?\s?\s)?([a-zA-Z])?(\s?\s?\s?\s)?(BIS|Bis|bis)?(\s?\s?\s?\s)?(\d\d?\d?)(\s?\s)?([a-zA-Z])?(\s?\s?\s?\s)?(\d\d)', r'\1 \3\5\7\9 \11\13 \15', linea)
            archivo_salida.write(linea_modificada)    
        

@document_router.get(
        path="/documentos/pendientes_carvajal",
        summary="Descarga un archivo con los pendientes de las ordenes solicitados",
)
def pendientes_carvajal(ordenInicial: int, ordenFinal: int, db: Session = Depends(get_session)):
    # Realiza la consulta SQLAlchemy y selecciona solo las columnas deseadas
    resultados = db.query(Historico.serial, Historico.cod_men, Historico.retorno).filter(
    Historico.orden >= ordenInicial,
    Historico.orden <= ordenFinal,
    Historico.cod_ent == 4000,  # Agrega esta condición,
    Historico.ret_esc == "i"
).all()
    # Reformatea los resultados para que tengan la forma correcta
    reformateados = [(row.serial, row.cod_men, row.retorno) for row in resultados]

    # Crea un DataFrame a partir de los resultados reformateados
    df = pd.DataFrame(reformateados, columns=['serial', 'cod_men', 'retorno'])

    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as temp_file:
        # Escribe el DataFrame en un archivo Excel
        df.to_excel(temp_file.name, index=False, sheet_name='Hoja1')

    # Devuelve el archivo Excel para descargar
    return FileResponse(temp_file.name, filename="pendientes.xlsx")



@document_router.get(
    path="/documentos/gestion",
    summary="Descarga un archivo con todos los envíos dentro de las fechas solicitadas formato aaaa.mm.dd",
    dependencies=[Depends(jwtBearer())]
)
def gestion(
    request: Request,
    fecha_inicial: str,
    fecha_final: str,
    db: Session = Depends(get_session)
):
    # Verificar la autenticación
    authorization = request.headers.get("Authorization")
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Esquema de autenticación inválido"
        )

    # Extraer el token sin el prefijo "Bearer"
    token = authorization.split(" ")[1]

    # Decodificar el token y obtener el payload
    payload = decodeJWT(token)

    # Obtener el ID de la compañía desde el payload
    companyID = payload['companyID']

    # Convertir las fechas a enteros para comparaciones
    fecha_inicial = int(fecha_inicial.replace(".", ""))
    fecha_final = int(fecha_final.replace(".", ""))

    # Seleccionar solo las columnas necesarias en la consulta de la base de datos
    columns = [Historico.serial, Historico.no_entidad, Historico.f_emi, Historico.orden, Historico.retorno, Historico.ret_esc, Historico.motivo]

    # Realizar la consulta en la base de datos
    resultados = filter_and_format_data(db, companyID, columns)

    # Crear un DataFrame a partir de los resultados
    df = create_dataframe(resultados)

    # Filtrar por fechas directamente en el DataFrame
    df = filter_by_dates(df, fecha_inicial, fecha_final)

    # Asignar valores a la columna 'estado' usando numpy.select
    df['estado'] = assign_status_column(df)

    # Seleccionar las columnas finales
    result_data = df[['serial', 'entidad', 'fecha_inicio', 'orden', 'estado']]

    # Convertir DataFrame a bytes y devolver los datos como una respuesta de transmisión
    return create_excel_response(result_data)



@document_router.post(
        path= "/gestionOrdenesCarvajal",
        summary="Se genera el rango de ordenes dentro de los cuales se debe hacer la predicción de entrega de los envíos",
        dependencies=[Depends(jwtBearer())]
        )
async def process_data(
    request: Request,
    orden_inicial: str = Query(..., description="Orden inicial"),
    orden_final: str = Query(..., description="Orden final"),
    db: Session = Depends(get_session)
):
    fecha = get_current_date()
    df, df_dirNum, df_cuenta, df_motivos = load_dataframes(ordenInicio=orden_inicial, ordenFin=orden_final)
    dfC = filter_dataframe(df, orden_inicial, orden_final)
    dfC = merge_and_fillna(dfC, df_dirNum, df_cuenta)
    dfC = apply_conditions(dfC)
    return merge_motivos_and_finalize(dfC, df_motivos, fecha)