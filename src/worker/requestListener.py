from fastapi import FastAPI

from database import dbManager
from utils.models import UserCredentials

app = FastAPI()


@app.get("/get-login-data/{service}")
def get_login_data(service: str):
    credentials = dbManager.get_credentials(service)
    return credentials


@app.post("/add-password/")
def add_password(credentials: UserCredentials):
    dbManager.add_credentials(credentials.service, credentials.login, credentials.password)


@app.delete("/delete-password/{service}/{login}")
def delete_password(service: str, login: str):
    dbManager.delete_credentials(service, login)
