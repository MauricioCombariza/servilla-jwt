# Esta linea es responsable por signing, encoding, decoding and returning jwt.
import time
import jwt
from decouple import config
from fastapi import HTTPException


JWT_SECRET = config("SECRET_KEY")
JWT_ALGORITHM = config("ALGORITHM")


# Esta función retorna los tokens generados
def token_response(token: str):
    return {
        "access token": token
    }

# Esta función firma los tokens


def signJWT(email: str, perfil: int, username: str):
    payload = {
        "userID": email,
        "perfilID": perfil,
        "username": username,
        "expiry": time.time() + 600
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    return token_response(token)

# Decode function debe devolver informacion teniendo el token

def decodeJWT(token):
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithm=JWT_ALGORITHM)
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail='Signature has expired')
        except jwt.InvalidTokenError as e:
            raise HTTPException(status_code=401, detail='Invalid token')
