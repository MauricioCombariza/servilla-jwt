from unirEntidades import combinar_archivos
import os

combinar_archivos('entidades/')

from unirArchivos import procesar_archivos

ruta_archivo = 'archivos/bancos.xlsx'

if os.path.exists(ruta_archivo):
    print(f"El archivo {ruta_archivo} existe.")
    procesar_archivos('archivos/base.xlsx', 'archivos/')
else:
    print(f"El archivo {ruta_archivo} no existe.")

from calcularConsolidado import calcularConsolidado

calcularConsolidado('archivo.xlsx')

from generacion_robot import generacion_robot

generacion_robot('consolidadoFinal.xlsx','contratos.xlsx')

# Borrar los archivos que se adjuntaron


