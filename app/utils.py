from __future__ import annotations

import streamlit as st

from config import DatabaseConfig
from db.connection import ConnectionManager


@st.cache_resource
def get_connection() -> ConnectionManager:
    config = DatabaseConfig.from_env()
    return ConnectionManager(config)


def extract_db_error(exc: Exception) -> str:
    msg = str(exc)
    marker = "SQL Server]"
    idx = msg.rfind(marker)
    if idx >= 0:
        rest = msg[idx + len(marker):]
        paren_idx = rest.find(" (")
        if paren_idx > 0:
            return rest[:paren_idx].strip()
        return rest.strip()
    return msg


def require_connection() -> ConnectionManager:
    try:
        conn = get_connection()
        if not conn.test_connection():
            st.error("Brak połączenia z bazą danych. Sprawdź plik .env.")
            st.stop()
        return conn
    except Exception as exc:
        st.error(f"Błąd konfiguracji połączenia: {exc}")
        st.info(
            "Sprawdź czy istnieje plik .env (przykład w .env.example), "
            "czy MS SQL Server jest uruchomiony i czy zainstalowany jest sterownik ODBC."
        )
        st.stop()
