from sqlalchemy import Integer, String
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped


class Base(DeclarativeBase):
    pass


class Credentials(Base):
    __tablename__ = 'credentials'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    service: Mapped[str] = mapped_column(String, nullable=False)
    login: Mapped[str] = mapped_column(String, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)


class Metadata(Base):
    __tablename__ = 'metadata'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_name: Mapped[str] = mapped_column(String, nullable=False)
    user_password: Mapped[str] = mapped_column(String, nullable=False)
    fernet_key: Mapped[str] = mapped_column(String, nullable=False)
