from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    serve_port: int


class MongoSettings(BaseSettings):
    mongo_host: str = "localhost"
    mongo_port: int = 27017


class SecuritySettings(BaseSettings):
    secret_key: str
    access_token_expire_minutes: int = 10
    algorith: str = "HS256"
    api_key: str
    api_key_name: str = "X-API-KEY"
    basic_password: str
    basic_username: str = "x-admin-user"
