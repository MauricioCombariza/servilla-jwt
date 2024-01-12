from fastapi import FastAPI, UploadFile, File, APIRouter
from pathlib import Path
import os
import glob
import zipfile
from io import BytesIO

# Asegúrate de que la carpeta "entidades" exista
os.makedirs("app/routes/Automate/entidades", exist_ok=True)
os.makedirs("app/routes/Automate/archivos", exist_ok=True)

async def new_entities(file: UploadFile = File(...)):
    # Guarda el archivo en la carpeta "entidades"
    file_path = os.path.join("app/routes/Automate/entidades", file.filename)
    with open(file_path, "wb") as file_object:
        file_object.write(file.file.read())

    # Ahora puedes usar el archivo en tu código, por ejemplo, imprimir el nombre del archivo
    return {"filename": file.filename, "saved_path": file_path}

async def new_files(file: UploadFile = File(...)):
    # Guarda el archivo en la carpeta "entidades"
    file_path = os.path.join("app/routes/Automate/archivos", file.filename)
    with open(file_path, "wb") as file_object:
        file_object.write(file.file.read())

    # Ahora puedes usar el archivo en tu código, por ejemplo, imprimir el nombre del archivo
    return {"filename": file.filename, "saved_path": file_path}

async def new_contracts(file: UploadFile = File(...)):
    # Guarda el archivo en la carpeta "entidades"
    file_path = os.path.join("app/routes/Automate", file.filename)
    with open(file_path, "wb") as file_object:
        file_object.write(file.file.read())

    # Ahora puedes usar el archivo en tu código, por ejemplo, imprimir el nombre del archivo
    return {"filename": file.filename, "saved_path": file_path}

def zip_files(directory: Path) -> BytesIO:
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, "w") as zip_file:
        for archivo in glob.glob(f'{directory}/*.xlsx'):
            archivo_nombre = os.path.basename(archivo)
            zip_file.write(archivo, archivo_nombre)
    buffer.seek(0)
    return buffer