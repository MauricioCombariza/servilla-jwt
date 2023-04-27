# Python
import shutil
import os
import re
from datetime import datetime
# Pydantic

# Fastapi
from fastapi.responses import StreamingResponse, FileResponse
from fastapi import APIRouter, Path, HTTPException, Form, File, UploadFile
from fastapi.params import Depends

# Terceros
from sqlalchemy.orm import Session
import pandas as pd
import numpy as np
from typing import List

# Modulos locales
from app.models.events import Historico
from app.database.connection import get_session, engine
from app.auth.jwt_bearer import jwtBearer
from app.database.lists.lists import regex


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
        
@document_router.post("/upload/")
def create_file(file: UploadFile = File(...)):
    global upload_folder
    upload_folder = '/mnt/c/Users/mcomb/OneDrive/Escritorio/Carvajal/python/pendientes'
    file_object = file.file
    #create empty file to copy the file_object to
    upload_folder = open(os.path.join(upload_folder, file.filename), 'wb+')
    shutil.copyfileobj(file_object, upload_folder)
    upload_folder.close()
    return {"filename": file.filename}