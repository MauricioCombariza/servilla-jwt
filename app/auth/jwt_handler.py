# Esta linea es responsable por signing, encoding, decoding and returning jwt.
import time
import jwt
from decouple import config

JWT_SECRET = config("SECRET_KEY")
JWT_ALGORITHM = config("ALGORITHM")


# Esta función retorna los tokens generados
def token_response(token: str):
    return {
        "access token": token
    }

# Esta función firma los tokens


def signJWT(email: str):
    payload = {
        "userID": email,
        "expiry": time.time() + 600
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    return token_response(token)

# Decode function debe devolver informacion teniendo el token


def decodeJWT(token: str):
    try:
        decode_token = jwt.decode(token, JWT_SECRET, algorithm=JWT_ALGORITHM)
        return decode_token if decode_token["expires"] >= time.time else None
    except:
        return {}
