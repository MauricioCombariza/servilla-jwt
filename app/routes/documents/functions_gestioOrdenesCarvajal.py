#Python
import io
import pytz

#FastAPI
from fastapi import APIRouter, Path, HTTPException, Form, File, UploadFile, Request, Query
from fastapi.responses import StreamingResponse, FileResponse

#Pandantic
from pydantic import BaseModel
from datetime import datetime

#Terceros
from sqlalchemy.orm import Session
import pandas as pd
import numpy as np

#Modulos locales
from app.database.connection import get_session, engine


class InputData(BaseModel):
    ordenInicio: int
    ordenFin: int

class OutputData(BaseModel):
    orden: int
    serial: str
    b: str
    c: str
    date: str

def get_current_date():
    bogota_timezone = pytz.timezone("America/Bogota")
    bogota_date = datetime.now(bogota_timezone)
    return bogota_date.strftime("%d/%m/%Y")

def load_dataframes(ordenInicio: int = Query(..., gt=0, description="Valor de ordenInicio"),
                    ordenFin: int = Query(..., gt=0, description="Valor de ordenFin")):
    try:
        data = f'''
            SELECT serial, no_entidad, orden, identdes, dirdes1, cod_sec,
                   dpto2, comentario, ret_esc, retorno, motivo, dir_num
            FROM histo
            WHERE LENGTH(serial) = 16
            AND orden BETWEEN {ordenInicio} AND {ordenFin};
        '''
        dfC = pd.read_sql_query(data, engine)
        
        dirNum_path = '/home/mauro/personalProjects/python/fastapi/servilla-jwt/app/routes/bases/dirNum.xlsx'
        cuenta_path = '/home/mauro/personalProjects/python/fastapi/servilla-jwt/app/routes/bases/cuenta.xlsx'
        motivo_path = '/home/mauro/personalProjects/python/fastapi/servilla-jwt/app/routes/bases/motivo.xlsx'

        df_dirNum = pd.read_excel(dirNum_path)
        df_cuenta = pd.read_excel(cuenta_path)
        df_motivos = pd.read_excel(motivo_path)

        return dfC, df_dirNum, df_cuenta, df_motivos
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error durante la carga de datos: {str(e)}")
    
def filter_dataframe(dfC, ordenInicio, ordenFin):
    dfC['serial'] = dfC['serial'].astype(str)
    dfC['orden'] = pd.to_numeric(dfC['orden'])
    # Convertir las variables a enteros
    ordenInicio = int(ordenInicio)
    ordenFin = int(ordenFin)
    
    dfC = dfC[(dfC['orden'] >= ordenInicio) & (dfC['orden'] <= ordenFin) & (dfC['serial'].apply(len) == 16)]
    dfC['dir_num'] = dfC['dir_num'].astype(str)
    return dfC

def merge_and_fillna(dfC, df_dirNum, df_cuenta):
    dfC_dirNum = pd.merge(dfC, df_dirNum, on='dir_num', how='left')
    dfC_dirNum['identdes'] = pd.to_numeric(dfC_dirNum['identdes'])
    df_cuenta['identdes'] = pd.to_numeric(df_cuenta['identdes'])
    dfC = pd.merge(dfC_dirNum, df_cuenta, on='identdes', how='left')

    conditions = [
    (dfC['motivo'] == 'Docto en Camino'),
    (dfC['ret_esc'] == 'E'),
    ((dfC['retorno'] == 'D') | (dfC['retorno'] == 'o'))
]
    choices = ['Docto en Camino', 'Entrega', dfC['motivo']]
    dfC['A'] = np.select(conditions, choices, default=0)

    return dfC

def apply_conditions(dfC):
    dfC['B'] = np.where(dfC['A'] == 0, np.where(dfC['resultado'] == 0, 0, dfC['resultado']), dfC['A'])
    dfC['C'] = np.where(dfC['B'] == 0, np.where(dfC['estadoCuenta'] == 0, 0, dfC['estadoCuenta']), dfC['B'])
    conditions = [
        (dfC['C'] == 0),
        (dfC['dpto2'] == 0),
        ((dfC['dpto2'] == 'OK') | (dfC['dpto2'] == 'ACT'))
    ]
    choices = [0, 0, 'Entrega']
    dfC['D'] = np.select(conditions, choices, default='Direccion Errada')
    
    return dfC


def merge_motivos_and_finalize(dfC, df_motivos, fecha):
    dfC = pd.merge(dfC, df_motivos, on='D', how='left')
    dfC['date'] = fecha
    dfC['orden'] = dfC['orden'].astype(int)
    dfC.loc[dfC['b'].isna(), ['b', 'c']] = [3, 1]
    dfC = dfC[['serial', 'b', 'c', 'date']]
    dfC = dfC[dfC['c'] != 'Eliminar']
    
    # Guardar el DataFrame en un objeto de bytes
    csv_data = dfC.to_csv(index=False, header=False).encode()
    
    return StreamingResponse(io.BytesIO(csv_data), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=output.csv"})
