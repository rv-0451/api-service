from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    serve_port: int


class MongoSettings(BaseSettings):
    mongo_host: str = "localhost"
    mongo_port: int = 27017
