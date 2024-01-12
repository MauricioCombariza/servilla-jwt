from pathlib import Path
import shutil

def borrar_archivos_en_carpeta(carpeta):
    # Obtener la ruta completa de la carpeta
    carpeta_path = Path(carpeta)

    # Iterar sobre los archivos en la carpeta
    for archivo in carpeta_path.glob('*'):
        try:
            # Intentar borrar el archivo
            if archivo.is_file():
                archivo.unlink()
        except Exception as e:
            print(f"No se pudo borrar {archivo}: {e}")

