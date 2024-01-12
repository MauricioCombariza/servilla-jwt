from fastapi import FastAPI, UploadFile, File, APIRouter, HTTPException
from fastapi.responses import FileResponse, StreamingResponse, JSONResponse
from app.routes.Automate.functions import new_entities, new_files, new_contracts, zip_files
from app.routes.Automate.unirEntidades import combinar_archivos
from app.routes.Automate.unirArchivos import procesar_archivos
from app.routes.Automate.calcularConsolidado import calcularConsolidado 
from app.routes.Automate.generacion_robot import generacion_robot 
from app.routes.Automate.funciones_generar_robot import create_robot_files, generate_robot_files, generate_single_robot_file 
from app.routes.Automate.borrar_archivos import borrar_archivos_en_carpeta
from pathlib import Path
import glob
import os

automate_router = APIRouter(
    tags=["Automate"]
)
# Asegúrate de que la carpeta "entidades" exista
os.makedirs("app/routes/Automate/entidades", exist_ok=True)

@automate_router.post("/entities/")
async def create_entities(file: UploadFile = File(...)):
    # Guarda el archivo en la carpeta "entidades"
    await new_entities(file)
    return print("Las entidades han subido de forma exitosa")

@automate_router.post("/archivos/")
async def create_files(file: UploadFile = File(...)):
    # Guarda el archivo en la carpeta "entidades"
    await new_files(file)
    return print("Los archivos han subido de forma exitosa")

@automate_router.post("/contratos/")
async def create_contracts(file: UploadFile = File(...)):
    # Guarda el archivo en la carpeta "entidades"
    await new_contracts(file)
    return print("Los contratos han subido de forma exitosa")

@automate_router.post("/unirEntidades/")
def unir_entidades():
    combinar_archivos('/entidades/')

@automate_router.post("/unirArchivos/")
def unir_archivos():
    script_directory = Path(__file__).parent
    ruta_archivo = script_directory/'archivos'/'bancos.xlsx'
       
    if os.path.exists(ruta_archivo):
        print(f"El archivo {ruta_archivo} existe.")
        procesar_archivos(script_directory/"archivos/base/base.xlsx",
                          script_directory/"archivos/",
                          resultado_excel=script_directory/"archivos/unionArchivos.xlsx",
                          excluir=script_directory/"archivos/contratos.xlsx")
    else:
        print(f"El archivo {ruta_archivo} no existe.")

@automate_router.post("/calcular_consolidado/")
def calcular_consolidado():
    
    script_directory = Path(__file__).parent
    calcularConsolidado(
        script_directory/"archivos/unionArchivos.xlsx",
        resultado_excel=script_directory/"archivos/consolidadoFinal.xlsx")
    
@automate_router.post("/borrar_archivos/")
def borrar_archivos():
    # Directorio del script
    script_directory = Path(__file__).parent

    # Carpetas a procesar
    carpetas_a_borrar = [
        script_directory / "archivos",
        script_directory / "entidades",
        script_directory / "robot",
    ]

    # Borrar archivos en cada carpeta
    for carpeta in carpetas_a_borrar:
        borrar_archivos_en_carpeta(carpeta)

    
# @automate_router.post("/robot/")
# def create_robot_files():
#     try:
#         script_directory = Path(__file__).parent
#         generacion_robot(
#             script_directory/"archivos/consolidadoFinal.xlsx",
#             script_directory/"archivos/contratos.xlsx",
#             script_directory/"archivos/base/robot.xlsx",
#             directorio=script_directory/"robot/")

#         directorio = script_directory/'robot'

#         buffer = zip_files(directorio)

#         if not buffer.getvalue():
#             return JSONResponse(content={"error": "El archivo ZIP está vacío"}, status_code=500)

#         return StreamingResponse(
#             content=buffer,
#             media_type="application/zip",
#             headers={"Content-Disposition": "attachment;filename=robot_files.zip"}
#         )
#     except Exception as e:
#         return JSONResponse(content={"error": f"Error en la generación del archivo ZIP: {str(e)}"}, status_code=500)        

@automate_router.post("/robot/")
def create_robot_files():
    try:
        script_directory = Path(__file__).parent
        generacion_robot(
            script_directory / "archivos/consolidadoFinal.xlsx",
            script_directory / "archivos/contratos.xlsx",
            script_directory / "archivos/base/robot.xlsx",
            directorio=script_directory / "robot/"
        )

        directorio = script_directory / 'robot'

        buffer = zip_files(directorio)

        if not buffer.getvalue():
            raise HTTPException(status_code=500, detail="El archivo ZIP está vacío")

        return StreamingResponse(
            content=iter([buffer.getvalue()]),
            media_type="application/zip",
            headers={
                "Content-Disposition": "attachment;filename=robot_files.zip"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en la generación del archivo ZIP: {str(e)}")
