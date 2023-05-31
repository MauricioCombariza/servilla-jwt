from pydantic import EmailStr

from fastapi import Request, Response
from fastapi.params import Depends
from fastapi import APIRouter, HTTPException, Form, status, Body

from app.database.connection import get_session
from app.models.users import User
from app.security.security import get_password_hash, verify_password
from app.schemas.schemas import UserLoginSchema
from app.auth.jwt_handler import signJWT, decodeJWT

from sqlalchemy.orm import Session

user_router = APIRouter(
    tags=["User"],
)


@user_router.get('/usuarios/')
def show_users(db: Session = Depends(get_session)):
    usuarios = db.query(User).all()
    return usuarios

@user_router.get('/me')
def decode_token(token:str) -> dict:
    return decodeJWT(token)


@user_router.post("/signup")
async def sign_user_up(db: Session = Depends(get_session),
                       email: EmailStr = Form(
        ...,
        title="Email o correo electrónico",
        description="Email con el que desea registrarse",
        example="mauricio.combariza@gruposervilla.com"),
    username: str = Form(
        ...,
        title="Usuario",
        description="Escriba el nombre de su usuario con una sola palabra",
        example="NombreApellido"),
    company: str = Form(
        ...,
        title="Compañia",
        description="Nombre de la compañia a la que pertenece",
        example="Servilla SAS"),
    password: str = Form(
        ...,
        title="Password o contraseña",
        description="Contraseña única de mínimo 6 caracteres y máximo 14",
        example="123456"),
    confirmPassword: str = Form(
        ...,
        title="Confirmar Password o contraseña",
        description="Contraseña única de mínimo 6 caracteres y máximo 14",
        example="123456"),


) -> dict:
    users = db.query(User).all()

    for user in users:
        if email == user.email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El email ya ha sido registrado!!"
            )

    if password != confirmPassword:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El password es diferente de su confirmación !!"
        )

    user = User(email=email, username=username, company=company, password=get_password_hash(password), activate=1, perfil=3)
    db.add(user)
    db.commit()
    return {
        "message": "El usuario ha sido registrado de forma existosa!"
    }


@user_router.post("/login")
async def sign_user_in(resp: Response,
                       db: Session = Depends(get_session),
                       email: EmailStr = Form(
        ...,
        title="Email o correo electrónico",
        description="Email con el que desea registrarse",
        example="mauricio.combariza@gruposervilla.com"),
    password: str = Form(
        ...,
        title="Password o contraseña",
        description="Contraseña única de mínimo 6 caracteres y máximo 14",
        example="123456")
) -> dict:
    users = db.query(User).all()
    for user in users:
        if (email == user.email) and verify_password(password, user.password):
            return signJWT(email, user.perfil)
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Verifique su email, password o que siga activo en la plataforma!!, haga click en registrarse!!"
        )
