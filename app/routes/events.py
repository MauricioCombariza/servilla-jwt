# Python
import shutil
import os
from datetime import datetime
# Pydantic

# Fastapi
from fastapi.responses import StreamingResponse
from fastapi import APIRouter, Path, HTTPException, Form
from fastapi.params import Depends

# Terceros
from sqlalchemy.orm import Session
import pandas as pd
import numpy as np

# Modulos locales
from app.models.events import Historico
from app.database.connection import get_session, engine
from app.auth.jwt_bearer import jwtBearer


event_router = APIRouter(
    tags=["Events"]
)


@event_router.get(
    path="/serial/{serial}",
    summary="Muestra el serial indicado",
    dependencies=[Depends(jwtBearer())]
)
async def get_serial(

    serial: str = Path(
        ...,
        description="Ingrese el numero serial que desea consultar",
        example="2208092647004648"
    ),
        db: Session = Depends(get_session)):
    serial = db.query(Historico).filter(Historico.serial == serial).all()

    if serial:
        return serial
    else:
        raise HTTPException(status_code=404, detail="Serial no encontrado")


@event_router.get(
    path="/dirnum/{dirnum}",
    summary="Muestra los resultados de una direccion numerica especifica",
    dependencies=[Depends(jwtBearer())]
)
async def get_dirnum(
    dirnum: str = Path(
        ...,
        description="Ingrese el numero de orden que desea buscar",
        example="130131003004100123"
    ),
    db: Session = Depends(get_session),
    limit: int = 10
):
    """
    Base de datos de Servilla

    Muestra todos los registros de una orden específica 

    Requerimientos:
        -

    """
    dirnum = db.query(Historico).filter(
        Historico.dir_num == dirnum).limit(limit).all()
    return dirnum

@event_router.get(
    path="/nombre/{name}",
    summary="Muestra los resultados de un nombre buscado"
)
async def get_name(
    name: str = Path(
        ...,
        description="Ingrese el nombre de la persona que desea buscar",
        example="Mauricio Combariza"
    ),
    db: Session = Depends(get_session),
    limit: int = 10
):
    """
    Base de datos de Servilla

    Muestra todos los registros de un nombre específico 

    Requerimientos:
        -

    """
    # name = db.query(Historico).filter(
    #     Historico.nombred == name).limit(limit).all()
    # return name

    name = db.query(Historico).filter(Historico.nombred.like(f'%{name}%')).limit(limit).all()
    return name
    # result = session.query(Customers).filter(Customers.name.like('Ra%'))

@event_router.get(
    path="/imagen/{orden}",
    summary="Trae todas las imagenes de una orden pedida",
    # dependencies=[Depends(jwtBearer())]
)
async def get_image(

    orden: str = Path(
        ...,
        description="Ingrese el numero de orden del cual quiera exportar sus imagenes",
        example="118895"
    ),
    db: Session = Depends(get_session)):
    
    data = 'SELECT * FROM histo  WHERE orden={}'.format(orden)
    
    

    if data:
        df = pd.read_sql(data, engine)
        # df.to_csv('/mnt/c/Imagenes/imagenes.csv', header=True, index=None, sep=',', mode='a')
        # return {'Message:', "Successfull pandas"}
        df = df[['serial', 'orden', 'f_esc', 'mot_esc', 'lot_esc', 'imagen']]
        df['imagen'] = df['imagen'].astype(str)
        df['lot_esc'] = df['lot_esc'].astype(str)
        orden = []
        serial = []
        for i in range(len(df)-1):
            if df.iloc[i, 4] != '':
                s = df.iloc[i, 2]
                for c in s:
                    if c == '.':
                        s = s.replace(c, "")
                x = r'V:\TRAB\{}\{}\{}.tif'.format(s,df.iloc[i,4], df.iloc[i,5])        
                # x = Path('V:', '/', 'TRAB', s, df.iloc[i,4], df.iloc[i,5] + ".tif")
                y = r"C:\Imagenes\Orden\{}.png".format(df.iloc[i,0][:16])
                # y = Path('C', '/'\, 'Imagenes', 'orden', df.iloc[i,0][:16] + ".png")
                # print(x)
                # a = os.chdir(x)
                # b = os.chdir(y)
                # shutil.copyfile(x,y)
                orden.append(x)
                serial.append(y)
        r = pd.DataFrame(orden, columns =['ruta'])
        s = pd.DataFrame(serial, columns =['destino'])
        result = pd.concat([r, s], axis=1)
        result.to_csv('/mnt/c/Imagenes/imagenes.csv', header=True, index=None, sep=',', mode='a')
        
        return {'Message:', "Successfull pandas"}
         
    else:
        raise HTTPException(status_code=404, detail="Orden no encontrada")
    

@event_router.post(
    path="/envios/",
    summary="Trae todas los envios de los courrier a nivel nacional",
    # dependencies=[Depends(jwtBearer())]
)
async def get_enviosCourrier(
    db: Session = Depends(get_session),
    fechaInicio: str = Form(
        ...,
        title="Fecha inicio",
        description="Ingrese la fecha desde la cual quiere ver los envios [yyyy-mm-dd]",
        example="2023-03-01"),
    fechaFin: str = Form(
        ...,
        title="Fecha final",
        description="Ingrese la fecha hasta la cual quiere ver los envios [yyyy-mm-dd]",
        example="2023-03-31"
    ),
    servicio: int = Form (
        ...,
        title="Numero del servicio del que desea el reporte",
        description="Numero de servicio",
        example=1010
    ),
    informe: int = Form(
        ...,
        title="Tipo de informe",
        description="Informe consolidado [1], por courrier [2]"
    )

) -> dict:
    df = pd.read_csv('/mnt/c/Users/mcomb/OneDrive/Escritorio/Carvajal/python/basesHisto.csv', low_memory=False)
    # data = 'SELECT * FROM histo'
    if df:
        # df = pd.read_sql(data, engine)
        # df = pd.read_csv('./basesHisto.csv', low_memory=False)
        format1 = '%Y.%m.%d'
        dfC = df.copy()
        dfC = dfC[['serial','no_entidad','servicio', 'orden','nombred', 'dirdes1', 'ciudad1', 'cod_sec',  'retorno','ret_esc',  'planilla',
                'f_emi', 'f_lleva', 'cod_men', 'dir_num', 'comentario',  'identdes']]
        Planilla = dfC['planilla'].notnull()
        dfC = dfC[Planilla]
        # dfC['cod_men'] = pd.to_numeric(dfC['cod_men'], errors='coerce').fillna(0).astype(np.int64)
        # MEN = dfC['cod_men'] > 729
        # dfC = dfC[MEN]
        SERVICIO = dfC['servicio'] == servicio
        dfC['fecha'] = dfC.apply(lambda x: datetime.strptime(x['f_emi'], format1).date(), axis=1)
        start_date = pd.to_datetime(fechaInicio).date()
        end_date = pd.to_datetime(fechaFin).date()
        INICIO = dfC['fecha'] > start_date
        FIN = dfC['fecha'] < end_date
        PEN = dfC['ret_esc'] == 'i'
        LLEV = dfC['ret_esc'] == 'p'
        RETL = dfC['retorno'] == 'l'
        RETP = dfC['retorno'] == 'p'
        dfC = dfC[SERVICIO]
        dfC = dfC[INICIO]
        dfC = dfC[((PEN | LLEV))]
        dfC = dfC[(RETL | RETP)]
        courriers = dfC['cod_men'].unique()
        if informe == 2:
            for i in range(len(courriers)):
                for j in range(len(dfC)):
                    options = [courriers[i]]
                    rslt_df = dfC[dfC['cod_men'].isin(options)]
                libro = '/mnt/c/Users/mcomb/OneDrive/Escritorio/Carvajal/python/courrier/pendientes/' + str(courriers[i]) + 'servicio_' + str(servicio) + 'long'+str(len(rslt_df)) + '.xlsx'
                rslt_df.iloc[:, 0:8].to_excel(libro, index=None)
        else:
            libro = '/mnt/c/Users/mcomb/OneDrive/Escritorio/Carvajal/python/courrier/pendientes/' + 'consolidado ' + 'servicio_' + str(servicio) + 'long'+str(len(dfC)) + '.xlsx'
            dfC.iloc[:, 0:8].to_excel(libro, index=None)        
    else:
        raise HTTPException(status_code=404, detail="Problemas en el servidor")


