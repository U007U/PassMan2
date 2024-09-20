import base64

import bcrypt
from cryptography.fernet import Fernet
from sqlalchemy import create_engine, select, insert, delete
from sqlalchemy.orm import sessionmaker

from database.dbModels import *

engine = create_engine("sqlite:///database.db")
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()


def register_user(username: str, password: str) -> None:
    key = Fernet.generate_key()
    encoded_key = base64.b64encode(key)

    encrypted_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    stmt = insert(Metadata).values(user_name=username, user_password=encrypted_password, fernet_key=encoded_key)
    session.execute(stmt)
    session.commit()


def login_user(username: str, password: str) -> bool:
    stmt = select(Metadata.user_name, Metadata.user_password)
    user_data = session.execute(stmt).fetchone()

    return username == user_data[0] and bcrypt.checkpw(password.encode(), user_data[1])


def validate_credentials(username: str, password: str) -> bool:
    stmt = select(Metadata.user_name, Metadata.user_password)
    result = session.execute(stmt).fetchall()[0]
    return username == result[0] and password == result[1]


def get_fernet_key() -> bytes:
    stmt = select(Metadata.fernet_key)
    result = session.execute(stmt).scalar()

    key = base64.b64decode(result)
    return key


def get_credentials(service: str) -> list:
    stmt = select(Credentials.login, Credentials.password).where(Credentials.service == service)
    credentials = session.execute(stmt).fetchall()

    result = []

    fernet = Fernet(get_fernet_key())
    for row in credentials:
        credential = {"login": row[0]}
        decoded_password = base64.b64decode(row[1])
        credential["password"] = (fernet.decrypt(decoded_password).decode())

        result.append(credential)

    return result


def add_credentials(service: str, login: str, password: str) -> None:
    fernet = Fernet(get_fernet_key())
    encoded_password = base64.b64encode(fernet.encrypt(password.encode()))

    stmt = insert(Credentials).values(service=service, login=login, password=encoded_password)
    session.execute(stmt)
    session.commit()


def delete_credentials(service: str, login: str) -> None:
    stmt = delete(Credentials).where((Credentials.service == service) & (Credentials.login == login))
    session.execute(stmt)
    session.commit()
