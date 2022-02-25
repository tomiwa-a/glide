from pydantic import BaseSettings

from app import database

class Settings(BaseSettings):
    database_hostname:str
    database_port:str
    database_password:str
    database_name:str
    database_username:str
    secret_key: str
    algorithm:str
    access_token_expire_minutes:int
    distance_matrix_api_key: str

    class Config:
        env_file = '.env'


settings = Settings()


