from __future__ import annotations

import streamlit as st

from db.repositories import ConferenceRepository, SessionRepository
from utils import require_connection


st.set_page_config(
    page_title="ConferenceDB — projekt zaliczeniowy",
    layout="wide",
)


def main() -> None:
    st.title("ConferenceDB")
    st.caption("System zarządzania konferencjami — projekt zaliczeniowy WSB Merito Gdańsk")

    conn = require_connection()
    st.sidebar.success("Połączono z bazą ConferenceDB")

    conf_repo = ConferenceRepository(conn)
    sess_repo = SessionRepository(conn)

    conferences = conf_repo.list_all()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Konferencji w bazie", len(conferences))
    c2.metric("Planned / Active", sum(1 for c in conferences if c.status in ("Active", "Planned")))
    c3.metric("Closed", sum(1 for c in conferences if c.status == "Closed"))
    c4.metric("Cancelled", sum(1 for c in conferences if c.status == "Cancelled"))

    st.divider()

    st.subheader("Najpopularniejsze sesje")
    st.caption("Widok `vw_PopularSessions` — liczy wypełnienie sali na podstawie zapisów")
    popular = sess_repo.popularity_dataframe()
    if popular.empty:
        st.info("Brak danych.")
    else:
        st.dataframe(popular.head(10), use_container_width=True, hide_index=True)

    st.divider()
    st.info(
        "Wybierz operację z paska bocznego:\n\n"
        "**Bilety** — zakup, anulowanie, przeglądanie\n\n"
        "**Harmonogram** — sesje konferencji i zapisy uczestników\n\n"
        "**Admin** — aktualizacja cen, przenoszenie sesji, raport konferencji\n\n"
        "**Zarządzanie** — dodawanie i edycja danych słownikowych"
    )


if __name__ == "__main__":
    main()
