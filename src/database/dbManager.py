import base64
from cryptography.fernet import Fernet
from sqlalchemy import create_engine, select, insert, delete
from sqlalchemy.orm import sessionmaker

from dbModels import *

engine = create_engine("sqlite:///database.db")
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()


def register_user(username: str, password: str) -> None:
    key = Fernet.generate_key()
    encoded_key = base64.b64encode(key)

    stmt = insert(Metadata).values(user_name=username, user_password=password, fernet_key=encoded_key)
    session.execute(stmt)
    session.commit()


def validate_credentials(username: str, password: str) -> bool:
    stmt = select(Metadata.user_name, Metadata.user_password)
    result = session.execute(stmt).fetchall()[0]
    return username == result[0] and password == result[1]


def get_fernet_key() -> bytes:
    stmt = select(Metadata.fernet_key)
    result = session.execute(stmt).scalar()

    try:
        key = base64.b64decode(result)
    except TypeError:
        raise Exception("You need to register in order to use the program!")

    return key


def get_credentials(service: str) -> list:
    stmt = select(Credentials.login, Credentials.password).where(Credentials.service == service)
    credentials = session.execute(stmt).fetchall()

    result = []

    fernet = Fernet(get_fernet_key())
    for row in credentials:
        credential = [row[0]]
        decoded_password = base64.b64decode(row[1])
        credential.append(fernet.decrypt(decoded_password).decode())

        result.append(credential)

    return result


def add_credentials(service: str, login: str, password: str) -> None:
    fernet = Fernet(get_fernet_key())
    encoded_password = base64.b64encode(fernet.encrypt(password.encode()))

    stmt = insert(Credentials).values(service=service, login=login, password=encoded_password)
    session.execute(stmt)
    session.commit()


def delete_credentials(service: str, login: str) -> None:
    stmt = delete(Credentials).where(Credentials.service == service and Credentials.login == login)
    session.execute(stmt)
    session.commit()
