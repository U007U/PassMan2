from pathlib import Path

from pydantic import BaseModel

BASE_DIR = Path(__file__).parent.parent


class UserCredentials(BaseModel):
    service: str
    login: str
    password: str


class Token(BaseModel):
    private_key_path: Path = BASE_DIR / "certs" / "private-key.pem"
    public_key_path: Path = BASE_DIR / "certs" / "public-key.pem"
    algorithm: str = "RS256"
