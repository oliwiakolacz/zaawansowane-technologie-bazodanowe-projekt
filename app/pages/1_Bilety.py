from __future__ import annotations

import streamlit as st

from db.repositories import (
    AttendeeRepository,
    ConferenceRepository,
    TicketRepository,
    TicketTypeRepository,
)
from services import TicketService
from utils import extract_db_error, require_connection


st.set_page_config(page_title="Bilety", layout="wide")
st.title("Bilety")

conn = require_connection()

conf_repo = ConferenceRepository(conn)
type_repo = TicketTypeRepository(conn)
attendee_repo = AttendeeRepository(conn)
ticket_repo = TicketRepository(conn)
ticket_service = TicketService(conn)

tab_purchase, tab_browse = st.tabs(["Zakup biletu", "Bilety uczestnika"])


with tab_purchase:
    st.subheader("Zakup nowego biletu")
    st.caption(
        "Wywołuje procedurę `usp_PurchaseTicket` — sprawdza okno sprzedaży, "
        "dostępność (`MaxQuantity` vs sprzedane), status konferencji."
    )

    conferences = conf_repo.list_all()
    if not conferences:
        st.warning("Brak konferencji w bazie.")
    else:
        conf_options = {f"{c.name} [{c.status}]": c.conference_id for c in conferences}
        selected_conf_label = st.selectbox("Konferencja", list(conf_options.keys()), key="purchase_conf")
        selected_conf_id = conf_options[selected_conf_label]

        ticket_types = type_repo.list_for_conference(selected_conf_id)
        if not ticket_types:
            st.info("Brak typów biletów dla wybranej konferencji.")
        else:
            type_options = {
                f"{tt.name} — {tt.price:.2f} PLN (sprzedaż: {tt.sales_start} → {tt.sales_end})": tt.ticket_type_id
                for tt in ticket_types
            }
            selected_type_label = st.selectbox("Typ biletu", list(type_options.keys()))
            selected_type_id = type_options[selected_type_label]

            avail = type_repo.availability(selected_type_id)
            a, b, c = st.columns(3)
            a.metric("Max", avail["max"])
            b.metric("Sprzedane", avail["sold"])
            c.metric("Dostępne", avail["available"])

            attendees = attendee_repo.list_all()
            att_options = {f"{a.full_name} ({a.email})": a.attendee_id for a in attendees}
            selected_att_label = st.selectbox("Uczestnik", list(att_options.keys()), key="purchase_att")
            selected_att_id = att_options[selected_att_label]

            if st.button("Kup bilet", type="primary"):
                try:
                    new_id = ticket_service.purchase(selected_type_id, selected_att_id)
                    st.success(f"Bilet kupiony. TicketID: **{new_id}**")
                    st.rerun()
                except Exception as exc:
                    st.error(f"Błąd: {extract_db_error(exc)}")


with tab_browse:
    st.subheader("Bilety wybranego uczestnika")
    st.caption(
        "Anulowanie biletu unieważnia także aktywne zapisy uczestnika "
        "na sesje danej konferencji (operacja transakcyjna)."
    )

    attendees = attendee_repo.list_all()
    if not attendees:
        st.warning("Brak uczestników w bazie.")
    else:
        att_options = {f"{a.full_name} ({a.email})": a.attendee_id for a in attendees}
        selected_label = st.selectbox("Uczestnik", list(att_options.keys()), key="browse_att")
        selected_id = att_options[selected_label]

        tickets = ticket_repo.list_for_attendee(selected_id)
        if not tickets:
            st.info("Ten uczestnik nie ma jeszcze biletów.")
        else:
            for t in tickets:
                with st.container(border=True):
                    cols = st.columns([3, 2, 2, 1])
                    cols[0].write(f"**TicketID:** {t.ticket_id} &nbsp;·&nbsp; **QR:** `{t.qr_code}`")
                    cols[1].write(f"**Cena:** {t.price:.2f} PLN")
                    cols[2].write(f"**Status:** `{t.status}`")
                    if t.status in ("Active", "Used"):
                        if cols[3].button("Anuluj", key=f"cancel_{t.ticket_id}"):
                            try:
                                ticket_service.cancel(t.ticket_id)
                                st.success(f"Bilet {t.ticket_id} anulowany.")
                                st.rerun()
                            except Exception as exc:
                                st.error(f"Błąd: {extract_db_error(exc)}")
