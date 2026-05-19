from __future__ import annotations

import streamlit as st

from db.repositories import (
    AttendeeRepository,
    ConferenceRepository,
    SessionRepository,
)
from services import RegistrationService
from utils import extract_db_error, require_connection


st.set_page_config(page_title="Harmonogram", layout="wide")
st.title("Harmonogram sesji")

conn = require_connection()

conf_repo = ConferenceRepository(conn)
sess_repo = SessionRepository(conn)
attendee_repo = AttendeeRepository(conn)
reg_service = RegistrationService(conn)


conferences = conf_repo.list_all()
if not conferences:
    st.warning("Brak konferencji w bazie.")
    st.stop()

conf_options = {f"{c.name} [{c.status}]": c.conference_id for c in conferences}
selected_conf_label = st.selectbox("Konferencja", list(conf_options.keys()))
selected_conf_id = conf_options[selected_conf_label]


st.subheader("Harmonogram")
st.caption("Widok `vw_SessionSchedule` — sala, prelegent, typ sesji, licznik zapisów.")

schedule_df = sess_repo.schedule_dataframe(selected_conf_id)
if schedule_df.empty:
    st.info("Brak sesji dla wybranej konferencji.")
else:
    st.dataframe(schedule_df, use_container_width=True, hide_index=True)


st.divider()


st.subheader("Zapis uczestnika na sesję")
st.caption(
    "Wywołuje procedurę `usp_RegisterForSession`. "
    "Jeśli sala pełna, trigger `trg_AutoWaitlist` automatycznie ustawi status na **Waitlist**."
)

sessions = sess_repo.list_for_conference(selected_conf_id)
if not sessions:
    st.info("Brak sesji dla tej konferencji.")
else:
    sess_options = {
        f"#{s.session_id} {s.title} ({s.start_time:%Y-%m-%d %H:%M})": s.session_id
        for s in sessions
    }
    selected_sess_label = st.selectbox("Sesja", list(sess_options.keys()))
    selected_sess_id = sess_options[selected_sess_label]

    eligible_attendees = attendee_repo.list_with_valid_ticket(selected_conf_id)
    if not eligible_attendees:
        st.warning(
            "Żaden uczestnik nie ma jeszcze ważnego biletu na tę konferencję. "
            "Najpierw kup bilet w zakładce **Bilety**."
        )
    else:
        att_options = {f"{a.full_name} ({a.email})": a.attendee_id for a in eligible_attendees}
        selected_att_label = st.selectbox("Uczestnik (tylko z ważnym biletem)", list(att_options.keys()))
        selected_att_id = att_options[selected_att_label]

        if st.button("Zapisz na sesję", type="primary"):
            try:
                status = reg_service.register(selected_sess_id, selected_att_id)
                if status == "Waitlist":
                    st.warning(
                        "Sala pełna — uczestnik dodany na **listę rezerwową** "
                        "(`trg_AutoWaitlist` zmienił status z Confirmed na Waitlist)."
                    )
                else:
                    st.success(f"Zapis potwierdzony. Status: **{status}**")
            except Exception as exc:
                st.error(f"Błąd: {extract_db_error(exc)}")
