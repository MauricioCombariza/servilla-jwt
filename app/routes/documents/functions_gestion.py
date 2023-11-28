# Python
import io

# Pydantic
# Fastapi
from fastapi.responses import StreamingResponse, FileResponse

# Terceros
import pandas as pd
import numpy as np

# Modulos locales
from app.models.events import Historico



def filter_and_format_data(db, companyID, columns):
    if companyID == 11:
        return db.query(*columns).order_by(Historico.orden.desc()).limit(50000).all()
    else:
        return db.query(*columns).filter(Historico.cod_ent == companyID).order_by(Historico.serial.desc()).limit(50000).all()


def create_dataframe(resultados):
    reformateados = [
        (row.serial, row.no_entidad, row.f_emi, row.orden, row.retorno, row.ret_esc, row.motivo)
        for row in resultados
    ]
    df = pd.DataFrame(reformateados, columns=['serial', 'entidad', 'fecha_inicio', 'orden', 'retorno', 'ret_esc', 'motivo'])
    df['fecha_inicio'] = df['fecha_inicio'].str.replace('.', '').astype(int)
    return df


def filter_by_dates(df, fecha_inicial, fecha_final):
    fechasFiltro = (df['fecha_inicio'] >= fecha_inicial) & (df['fecha_inicio'] <= fecha_final)
    return df[fechasFiltro]


def assign_status_column(df):
    conditions = [
        (df['ret_esc'] == 'E') | (df['retorno'] == 'E'),
        (df['retorno'] == 'f'),
        (df['retorno'] == 'o'),
        (df['retorno'] == 'D'),
        (df['ret_esc'] == 'i') & df['retorno'].isin(['l', 'j']),
        (df['retorno'] == 'i')
    ]
    choices = ['Entrega', 'Envío no ha llegado, faltante', 'Devolución en proceso', 'Motivo', 'Distribución', 'Alistamiento']
    return np.select(conditions, choices, default='Otro')


def create_excel_response(result_data):
    excel_bytes_io = io.BytesIO()
    with pd.ExcelWriter(excel_bytes_io, engine='openpyxl', mode='w') as writer:
        result_data.to_excel(writer, index=False, sheet_name='Hoja1')
    return StreamingResponse(iter([excel_bytes_io.getvalue()]), media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition": "attachment;filename=gestion.xlsx"})
