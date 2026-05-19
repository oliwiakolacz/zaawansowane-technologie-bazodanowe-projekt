from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


class ConfigError(RuntimeError):
    pass


@dataclass(frozen=True)
class DatabaseConfig:
    server: str
    database: str
    user: str
    password: str
    port: int = 1433
    driver: str = "ODBC Driver 18 for SQL Server"
    trust_cert: bool = True
    encrypt: bool = True

    @classmethod
    def from_env(cls) -> "DatabaseConfig":
        required = ("DB_SERVER", "DB_NAME", "DB_USER", "DB_PASSWORD")
        missing = [k for k in required if not os.environ.get(k)]
        if missing:
            raise ConfigError(
                f"Brakujące zmienne środowiskowe: {', '.join(missing)}. "
                f"Skopiuj .env.example jako .env i uzupełnij wartości."
            )
        return cls(
            server=os.environ["DB_SERVER"],
            database=os.environ["DB_NAME"],
            user=os.environ["DB_USER"],
            password=os.environ["DB_PASSWORD"],
            port=int(os.environ.get("DB_PORT", "1433")),
            driver=os.environ.get("DB_DRIVER", "ODBC Driver 18 for SQL Server"),
            trust_cert=os.environ.get("DB_TRUST_CERT", "yes").lower() in ("yes", "true", "1"),
            encrypt=os.environ.get("DB_ENCRYPT", "yes").lower() in ("yes", "true", "1"),
        )

    def connection_string(self) -> str:
        return (
            f"DRIVER={{{self.driver}}};"
            f"SERVER={self.server},{self.port};"
            f"DATABASE={self.database};"
            f"UID={self.user};"
            f"PWD={self.password};"
            f"Encrypt={'yes' if self.encrypt else 'no'};"
            f"TrustServerCertificate={'yes' if self.trust_cert else 'no'};"
        )
