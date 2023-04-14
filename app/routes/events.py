# Python
import shutil
import os

# Pydantic

# Fastapi
from fastapi.responses import StreamingResponse
from fastapi import APIRouter, Path, HTTPException
from fastapi.params import Depends

# Terceros
from sqlalchemy.orm import Session
import pandas as pd

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
    # dependencies=[Depends(jwtBearer())]
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
    summary="Muestra los resultados de una direccion numerica especifica"
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



