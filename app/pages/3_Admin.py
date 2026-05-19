from __future__ import annotations

from decimal import Decimal

import pandas as pd
import streamlit as st

from db.repositories import (
    ConferenceRepository,
    RoomRepository,
    SessionRepository,
    TicketTypeRepository,
)
from services import AdminService, TicketService
from utils import extract_db_error, require_connection


st.set_page_config(page_title="Admin", layout="wide")
st.title("Operacje administracyjne")

conn = require_connection()

conf_repo = ConferenceRepository(conn)
type_repo = TicketTypeRepository(conn)
sess_repo = SessionRepository(conn)
room_repo = RoomRepository(conn)
ticket_service = TicketService(conn)
admin_service = AdminService(conn)


tab_price, tab_reassign, tab_report = st.tabs([
    "Aktualizacja ceny biletu",
    "Przeniesienie sesji",
    "Raport konferencji",
])


with tab_price:
    st.subheader("Aktualizacja ceny typu biletu")
    st.caption(
        "Trigger `trg_PriceHistoryAudit` automatycznie zapisze starą i nową cenę w `PriceHistory` "
        "— niezależnie od tego, którą ścieżką wykonana jest aktualizacja."
    )

    conferences = conf_repo.list_all()
    if conferences:
        conf_options = {f"{c.name} [{c.status}]": c.conference_id for c in conferences}
        selected_label = st.selectbox("Konferencja", list(conf_options.keys()), key="price_conf")
        selected_conf_id = conf_options[selected_label]

        types = type_repo.list_for_conference(selected_conf_id)
        if not types:
            st.info("Brak typów biletów dla wybranej konferencji.")
        else:
            type_options = {f"{tt.name} (aktualna: {tt.price:.2f} PLN)": tt for tt in types}
            selected_type_label = st.selectbox("Typ biletu", list(type_options.keys()))
            selected_tt = type_options[selected_type_label]

            new_price = st.number_input(
                "Nowa cena (PLN)",
                min_value=0.0,
                value=float(selected_tt.price),
                step=10.0,
                format="%.2f",
            )

            if st.button("Zmień cenę", type="primary", key="update_price_btn"):
                try:
                    ticket_service.update_price(selected_tt.ticket_type_id, Decimal(str(new_price)))
                    st.success(
                        f"Cena zmieniona z {selected_tt.price:.2f} na {new_price:.2f} PLN. "
                        f"Wpis dodany do `PriceHistory` przez trigger."
                    )
                    st.rerun()
                except Exception as exc:
                    st.error(f"Błąd: {extract_db_error(exc)}")


with tab_reassign:
    st.subheader("Przeniesienie sesji do innej sali")
    st.caption(
        "Przed zmianą sali aplikacja sprawdza, czy w nowej sali nie ma już innej sesji w tym samym czasie."
    )

    conferences = conf_repo.list_all()
    if conferences:
        conf_options = {f"{c.name} [{c.status}]": c.conference_id for c in conferences}
        selected_label = st.selectbox("Konferencja", list(conf_options.keys()), key="reassign_conf")
        selected_conf_id = conf_options[selected_label]

        sessions = sess_repo.list_for_conference(selected_conf_id)
        if not sessions:
            st.info("Brak sesji dla wybranej konferencji.")
        else:
            sess_options = {
                f"#{s.session_id} {s.title} ({s.start_time:%H:%M}–{s.end_time:%H:%M}, RoomID={s.room_id})": s.session_id
                for s in sessions
            }
            selected_sess_label = st.selectbox("Sesja", list(sess_options.keys()))
            selected_sess_id = sess_options[selected_sess_label]

            rooms = room_repo.list_all()
            room_options = {f"{r.name} (cap {r.capacity})": r.room_id for r in rooms}
            selected_room_label = st.selectbox("Nowa sala", list(room_options.keys()))
            selected_room_id = room_options[selected_room_label]

            if st.button("Przenieś sesję", type="primary"):
                try:
                    admin_service.reassign_session(selected_sess_id, selected_room_id)
                    st.success(f"Sesja #{selected_sess_id} przeniesiona do sali ID {selected_room_id}.")
                    st.rerun()
                except Exception as exc:
                    st.error(f"Błąd: {extract_db_error(exc)}")


with tab_report:
    st.subheader("Raport konferencji")
    st.caption(
        "Raport agreguje dane konferencji: przegląd, sprzedaż biletów per typ, "
        "top sesje wg liczby zapisów."
    )

    conferences = conf_repo.list_all()
    if conferences:
        conf_options = {f"{c.name} [{c.status}]": c.conference_id for c in conferences}
        selected_label = st.selectbox("Konferencja", list(conf_options.keys()), key="report_conf")
        selected_conf_id = conf_options[selected_label]

        if st.button("Generuj raport", type="primary"):
            try:
                report = admin_service.conference_report(selected_conf_id)

                st.markdown("#### Przegląd konferencji")
                if report["overview"]:
                    st.dataframe(pd.DataFrame(report["overview"]), use_container_width=True, hide_index=True)
                else:
                    st.info("Brak danych.")

                st.markdown("#### Sprzedaż biletów (per typ)")
                if report["tickets"]:
                    st.dataframe(pd.DataFrame(report["tickets"]), use_container_width=True, hide_index=True)
                else:
                    st.info("Brak danych.")

                st.markdown("#### Top sesje (wg liczby zapisów)")
                if report["top_sessions"]:
                    st.dataframe(pd.DataFrame(report["top_sessions"]), use_container_width=True, hide_index=True)
                else:
                    st.info("Brak danych.")

            except Exception as exc:
                st.error(f"Błąd: {extract_db_error(exc)}")
