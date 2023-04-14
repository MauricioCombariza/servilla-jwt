from pydantic import BaseModel, Field, EmailStr


class UserSchema(BaseModel):
    fullname: str = Field(default=None)
    email: EmailStr = Field(default=None)
    password: str = Field(default=None)

    class Config:
        the_schema = {
            "user_demo": {
                "username": "Mauricio",
                "email": "mcombarizav@gmail.com",
                "password": "123456",
                "activate": 1,
                "perfil": 3,
                "company": "Servilla"
            }
        }


class UserLoginSchema(BaseModel):
    email: EmailStr = Field(default=None)
    password: str = Field(default=None)

    class Config:
        the_schema = {
            "user_demo": {
                "email": "mcombarizav@gmail.com",
                "password": "123456"
            }
        }
