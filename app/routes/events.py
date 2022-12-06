# Python

# Pydantic

# Fastapi
from fastapi import APIRouter, Path, HTTPException
from fastapi.params import Depends

# Terceros
from sqlalchemy.orm import Session

# Modulos locales
from app.models.events import Historico
from app.database.connection import get_session
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
    serial = db.query(Historico).filter(Historico.serial == serial).one()

    if serial:
        return serial
    else:
        raise HTTPException(status_code=404, detail="Serial no encontrado")
