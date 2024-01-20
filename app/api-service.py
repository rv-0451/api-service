import uvicorn
import logging.config
from utils.logger import LOGGING_CONFIG
from fastapi import FastAPI
from v1.routers import data, search
from core.settings import AppSettings


logging.config.dictConfig(LOGGING_CONFIG)


app_settings = AppSettings()


app = FastAPI()
app.include_router(data.router)
app.include_router(search.router)


if __name__ == "__main__":
    uvicorn.run("api-service:app", host="0.0.0.0", port=app_settings.serve_port)
