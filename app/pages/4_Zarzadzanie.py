from __future__ import annotations

from datetime import date, datetime, time
from decimal import Decimal

import pandas as pd
import streamlit as st

from db.repositories import (
    AttendeeRepository,
    ConferenceRepository,
    RoomRepository,
    SessionRepository,
    SpeakerRepository,
    TicketTypeRepository,
    TrackRepository,
)
from utils import extract_db_error, require_connection


st.set_page_config(page_title="Zarządzanie", layout="wide")
st.title("Zarządzanie danymi")

conn = require_connection()

attendee_repo = AttendeeRepository(conn)
conf_repo = ConferenceRepository(conn)
room_repo = RoomRepository(conn)
sess_repo = SessionRepository(conn)
speaker_repo = SpeakerRepository(conn)
type_repo = TicketTypeRepository(conn)
track_repo = TrackRepository(conn)


tab_attendees, tab_speakers, tab_rooms, tab_confs, tab_tracks, tab_types, tab_sessions = st.tabs([
    "Uczestnicy",
    "Prelegenci",
    "Sale",
    "Konferencje",
    "Ścieżki tematyczne",
    "Typy biletów",
    "Sesje",
])


with tab_attendees:
    st.subheader("Lista uczestników")
    attendees = attendee_repo.list_all()
    if attendees:
        df = pd.DataFrame([{
            "ID": a.attendee_id,
            "Imię": a.first_name,
            "Nazwisko": a.last_name,
            "Email": a.email,
            "Firma": a.company or "—",
            "Zarejestrowany": a.registration_date.strftime("%Y-%m-%d %H:%M") if a.registration_date else "—",
        } for a in attendees])
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("Brak uczestników w bazie.")

    st.divider()

    st.subheader("Dodaj nowego uczestnika")
    with st.form("add_attendee_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            a_first = st.text_input("Imię *")
            a_email = st.text_input("Email *")
        with c2:
            a_last = st.text_input("Nazwisko *")
            a_company = st.text_input("Firma (opcjonalnie)")
        if st.form_submit_button("Dodaj uczestnika", type="primary"):
            if not (a_first and a_last and a_email):
                st.error("Imię, Nazwisko i Email są wymagane.")
            else:
                try:
                    new_id = attendee_repo.create(a_first, a_last, a_email, a_company or None)
                    st.success(f"Uczestnik dodany. AttendeeID: **{new_id}**")
                    st.rerun()
                except Exception as exc:
                    st.error(f"Błąd: {extract_db_error(exc)}")

    st.divider()

    st.subheader("Edytuj / usuń uczestnika")
    if attendees:
        edit_options = {f"#{a.attendee_id} {a.full_name} ({a.email})": a for a in attendees}
        sel_label = st.selectbox("Wybierz uczestnika", list(edit_options.keys()), key="edit_att_sel")
        sel_att = edit_options[sel_label]

        with st.form("edit_attendee_form"):
            c1, c2 = st.columns(2)
            with c1:
                e_first = st.text_input("Imię", value=sel_att.first_name)
                e_email = st.text_input("Email", value=sel_att.email)
            with c2:
                e_last = st.text_input("Nazwisko", value=sel_att.last_name)
                e_company = st.text_input("Firma", value=sel_att.company or "")
            if st.form_submit_button("Zapisz zmiany", type="primary"):
                try:
                    attendee_repo.update(sel_att.attendee_id, e_first, e_last, e_email, e_company or None)
                    st.success("Zmiany zapisane.")
                    st.rerun()
                except Exception as exc:
                    st.error(f"Błąd: {extract_db_error(exc)}")

        confirm_del = st.checkbox("Tak, na pewno chcę usunąć tego uczestnika", key=f"confirm_del_att_{sel_att.attendee_id}")
        if st.button("Usuń uczestnika", type="secondary", disabled=not confirm_del, key=f"del_att_{sel_att.attendee_id}"):
            try:
                attendee_repo.delete(sel_att.attendee_id)
                st.success(f"Uczestnik #{sel_att.attendee_id} usunięty.")
                st.rerun()
            except Exception as exc:
                st.error(f"Błąd: {extract_db_error(exc)} (uczestnik prawdopodobnie ma powiązane bilety lub zapisy).")


with tab_speakers:
    st.subheader("Lista prelegentów")
    speakers = speaker_repo.list_all()
    if speakers:
        df = pd.DataFrame([{
            "ID": s.speaker_id,
            "Imię": s.first_name,
            "Nazwisko": s.last_name,
            "Email": s.email,
            "Kraj": s.country or "—",
            "Firma": s.company or "—",
        } for s in speakers])
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("Brak prelegentów w bazie.")

    st.divider()

    st.subheader("Dodaj nowego prelegenta")
    with st.form("add_speaker_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            s_first = st.text_input("Imię *", key="add_sp_first")
            s_email = st.text_input("Email *", key="add_sp_email")
            s_country = st.text_input("Kraj (opcjonalnie)", key="add_sp_country")
        with c2:
            s_last = st.text_input("Nazwisko *", key="add_sp_last")
            s_company = st.text_input("Firma (opcjonalnie)", key="add_sp_company")
        if st.form_submit_button("Dodaj prelegenta", type="primary"):
            if not (s_first and s_last and s_email):
                st.error("Imię, Nazwisko i Email są wymagane.")
            else:
                try:
                    new_id = speaker_repo.create(s_first, s_last, s_email,
                                                  s_country or None, s_company or None)
                    st.success(f"Prelegent dodany. SpeakerID: **{new_id}**")
                    st.rerun()
                except Exception as exc:
                    st.error(f"Błąd: {extract_db_error(exc)}")

    st.divider()

    st.subheader("Edytuj / usuń prelegenta")
    if speakers:
        edit_options = {f"#{s.speaker_id} {s.full_name} ({s.email})": s for s in speakers}
        sel_label = st.selectbox("Wybierz prelegenta", list(edit_options.keys()), key="edit_sp_sel")
        sel_sp = edit_options[sel_label]

        with st.form("edit_speaker_form"):
            c1, c2 = st.columns(2)
            with c1:
                e_first = st.text_input("Imię", value=sel_sp.first_name)
                e_email = st.text_input("Email", value=sel_sp.email)
                e_country = st.text_input("Kraj", value=sel_sp.country or "")
            with c2:
                e_last = st.text_input("Nazwisko", value=sel_sp.last_name)
                e_company = st.text_input("Firma", value=sel_sp.company or "")
            if st.form_submit_button("Zapisz zmiany", type="primary"):
                try:
                    speaker_repo.update(sel_sp.speaker_id, e_first, e_last, e_email,
                                        e_country or None, e_company or None)
                    st.success("Zmiany zapisane.")
                    st.rerun()
                except Exception as exc:
                    st.error(f"Błąd: {extract_db_error(exc)}")

        confirm_del = st.checkbox("Tak, na pewno chcę usunąć tego prelegenta", key=f"confirm_del_sp_{sel_sp.speaker_id}")
        if st.button("Usuń prelegenta", type="secondary", disabled=not confirm_del, key=f"del_sp_{sel_sp.speaker_id}"):
            try:
                speaker_repo.delete(sel_sp.speaker_id)
                st.success(f"Prelegent #{sel_sp.speaker_id} usunięty.")
                st.rerun()
            except Exception as exc:
                st.error(f"Błąd: {extract_db_error(exc)} (prelegent prawdopodobnie ma powiązane sesje).")


with tab_rooms:
    st.subheader("Lista sal")
    rooms = room_repo.list_all()
    if rooms:
        df = pd.DataFrame([{
            "ID": r.room_id,
            "Nazwa": r.name,
            "Pojemność": r.capacity,
            "Piętro": r.floor,
            "Projektor": "Tak" if r.has_projector else "Nie",
        } for r in rooms])
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("Brak sal w bazie.")

    st.divider()

    st.subheader("Dodaj nową salę")
    with st.form("add_room_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            r_name = st.text_input("Nazwa *")
            r_floor = st.number_input("Piętro", value=0, step=1)
        with c2:
            r_capacity = st.number_input("Pojemność *", min_value=1, value=50, step=10)
            r_projector = st.checkbox("Projektor", value=True)
        if st.form_submit_button("Dodaj salę", type="primary"):
            if not r_name:
                st.error("Nazwa sali jest wymagana.")
            else:
                try:
                    new_id = room_repo.create(r_name, int(r_capacity), int(r_floor), r_projector)
                    st.success(f"Sala dodana. RoomID: **{new_id}**")
                    st.rerun()
                except Exception as exc:
                    st.error(f"Błąd: {extract_db_error(exc)}")

    st.divider()

    st.subheader("Edytuj / usuń salę")
    if rooms:
        edit_options = {f"#{r.room_id} {r.name} (cap {r.capacity})": r for r in rooms}
        sel_label = st.selectbox("Wybierz salę", list(edit_options.keys()), key="edit_room_sel")
        sel_r = edit_options[sel_label]

        with st.form("edit_room_form"):
            c1, c2 = st.columns(2)
            with c1:
                e_name = st.text_input("Nazwa", value=sel_r.name)
                e_floor = st.number_input("Piętro", value=sel_r.floor, step=1)
            with c2:
                e_capacity = st.number_input("Pojemność", min_value=1, value=sel_r.capacity, step=10)
                e_projector = st.checkbox("Projektor", value=sel_r.has_projector)
            if st.form_submit_button("Zapisz zmiany", type="primary"):
                try:
                    room_repo.update(sel_r.room_id, e_name, int(e_capacity), int(e_floor), e_projector)
                    st.success("Zmiany zapisane.")
                    st.rerun()
                except Exception as exc:
                    st.error(f"Błąd: {extract_db_error(exc)}")

        confirm_del = st.checkbox("Tak, na pewno chcę usunąć tę salę", key=f"confirm_del_room_{sel_r.room_id}")
        if st.button("Usuń salę", type="secondary", disabled=not confirm_del, key=f"del_room_{sel_r.room_id}"):
            try:
                room_repo.delete(sel_r.room_id)
                st.success(f"Sala #{sel_r.room_id} usunięta.")
                st.rerun()
            except Exception as exc:
                st.error(f"Błąd: {extract_db_error(exc)} (sala prawdopodobnie ma przypisane sesje).")


with tab_confs:
    st.subheader("Lista konferencji")
    confs = conf_repo.list_all()
    if confs:
        df = pd.DataFrame([{
            "ID": c.conference_id,
            "Nazwa": c.name,
            "Start": c.start_date,
            "Koniec": c.end_date,
            "Lokalizacja": c.location,
            "Max uczestników": c.max_attendees,
            "Status": c.status,
        } for c in confs])
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("Brak konferencji w bazie.")

    st.divider()

    st.subheader("Dodaj nową konferencję")
    with st.form("add_conf_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            cf_name = st.text_input("Nazwa *")
            cf_start = st.date_input("Data rozpoczęcia *", value=date.today())
            cf_location = st.text_input("Lokalizacja *")
        with c2:
            cf_status = st.selectbox("Status", ["Planned", "Active", "Closed", "Cancelled"])
            cf_end = st.date_input("Data zakończenia *", value=date.today())
            cf_max = st.number_input("Max uczestników *", min_value=1, value=500, step=50)
        if st.form_submit_button("Dodaj konferencję", type="primary"):
            if not (cf_name and cf_location):
                st.error("Nazwa i Lokalizacja są wymagane.")
            elif cf_end < cf_start:
                st.error("Data zakończenia nie może być wcześniejsza niż data rozpoczęcia.")
            else:
                try:
                    new_id = conf_repo.create(cf_name, cf_start, cf_end, cf_location,
                                              int(cf_max), cf_status)
                    st.success(f"Konferencja dodana. ConferenceID: **{new_id}**")
                    st.rerun()
                except Exception as exc:
                    st.error(f"Błąd: {extract_db_error(exc)}")

    st.divider()

    st.subheader("Edytuj / usuń konferencję")
    if confs:
        edit_options = {f"#{c.conference_id} {c.name} [{c.status}]": c for c in confs}
        sel_label = st.selectbox("Wybierz konferencję", list(edit_options.keys()), key="edit_conf_sel")
        sel_c = edit_options[sel_label]

        with st.form("edit_conf_form"):
            c1, c2 = st.columns(2)
            with c1:
                e_name = st.text_input("Nazwa", value=sel_c.name)
                e_start = st.date_input("Data rozpoczęcia", value=sel_c.start_date)
                e_location = st.text_input("Lokalizacja", value=sel_c.location)
            with c2:
                statuses = ["Planned", "Active", "Closed", "Cancelled"]
                e_status = st.selectbox("Status", statuses, index=statuses.index(sel_c.status))
                e_end = st.date_input("Data zakończenia", value=sel_c.end_date)
                e_max = st.number_input("Max uczestników", min_value=1, value=sel_c.max_attendees, step=50)
            if st.form_submit_button("Zapisz zmiany", type="primary"):
                if e_end < e_start:
                    st.error("Data zakończenia nie może być wcześniejsza niż data rozpoczęcia.")
                else:
                    try:
                        conf_repo.update(sel_c.conference_id, e_name, e_start, e_end,
                                         e_location, int(e_max), e_status)
                        st.success("Zmiany zapisane.")
                        st.rerun()
                    except Exception as exc:
                        st.error(f"Błąd: {extract_db_error(exc)}")

        confirm_del = st.checkbox("Tak, na pewno chcę usunąć tę konferencję", key=f"confirm_del_conf_{sel_c.conference_id}")
        if st.button("Usuń konferencję", type="secondary", disabled=not confirm_del, key=f"del_conf_{sel_c.conference_id}"):
            try:
                conf_repo.delete(sel_c.conference_id)
                st.success(f"Konferencja #{sel_c.conference_id} usunięta.")
                st.rerun()
            except Exception as exc:
                st.error(f"Błąd: {extract_db_error(exc)} (konferencja prawdopodobnie ma powiązane sesje/bilety/ścieżki).")


with tab_tracks:
    st.subheader("Lista ścieżek tematycznych")
    tracks = track_repo.list_all()
    confs_for_select = conf_repo.list_all()
    conf_by_id = {c.conference_id: c for c in confs_for_select}

    if tracks:
        df = pd.DataFrame([{
            "ID": t.track_id,
            "Konferencja": conf_by_id[t.conference_id].name if t.conference_id in conf_by_id else f"ID {t.conference_id}",
            "Nazwa": t.name,
            "Opis": t.description or "—",
        } for t in tracks])
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("Brak ścieżek tematycznych w bazie.")

    st.divider()

    st.subheader("Dodaj nową ścieżkę")
    if not confs_for_select:
        st.warning("Najpierw musi istnieć przynajmniej jedna konferencja.")
    else:
        with st.form("add_track_form", clear_on_submit=True):
            conf_options = {f"{c.name}": c.conference_id for c in confs_for_select}
            t_conf_label = st.selectbox("Konferencja *", list(conf_options.keys()), key="add_track_conf")
            t_conf_id = conf_options[t_conf_label]
            t_name = st.text_input("Nazwa ścieżki *")
            t_desc = st.text_area("Opis (opcjonalnie)")
            if st.form_submit_button("Dodaj ścieżkę", type="primary"):
                if not t_name:
                    st.error("Nazwa ścieżki jest wymagana.")
                else:
                    try:
                        new_id = track_repo.create(t_conf_id, t_name, t_desc or None)
                        st.success(f"Ścieżka dodana. TrackID: **{new_id}**")
                        st.rerun()
                    except Exception as exc:
                        st.error(f"Błąd: {extract_db_error(exc)}")

    st.divider()

    st.subheader("Edytuj / usuń ścieżkę")
    if tracks and confs_for_select:
        edit_options = {
            f"#{t.track_id} {t.name} ({conf_by_id[t.conference_id].name if t.conference_id in conf_by_id else 'ID ' + str(t.conference_id)})": t
            for t in tracks
        }
        sel_label = st.selectbox("Wybierz ścieżkę", list(edit_options.keys()), key="edit_track_sel")
        sel_t = edit_options[sel_label]

        with st.form("edit_track_form"):
            conf_options = {f"{c.name}": c.conference_id for c in confs_for_select}
            current_conf_label = next((k for k, v in conf_options.items() if v == sel_t.conference_id), list(conf_options.keys())[0])
            e_conf_label = st.selectbox("Konferencja", list(conf_options.keys()),
                                         index=list(conf_options.keys()).index(current_conf_label),
                                         key="edit_track_conf")
            e_conf_id = conf_options[e_conf_label]
            e_name = st.text_input("Nazwa", value=sel_t.name)
            e_desc = st.text_area("Opis", value=sel_t.description or "")
            if st.form_submit_button("Zapisz zmiany", type="primary"):
                try:
                    track_repo.update(sel_t.track_id, e_conf_id, e_name, e_desc or None)
                    st.success("Zmiany zapisane.")
                    st.rerun()
                except Exception as exc:
                    st.error(f"Błąd: {extract_db_error(exc)}")

        confirm_del = st.checkbox("Tak, na pewno chcę usunąć tę ścieżkę", key=f"confirm_del_track_{sel_t.track_id}")
        if st.button("Usuń ścieżkę", type="secondary", disabled=not confirm_del, key=f"del_track_{sel_t.track_id}"):
            try:
                track_repo.delete(sel_t.track_id)
                st.success(f"Ścieżka #{sel_t.track_id} usunięta.")
                st.rerun()
            except Exception as exc:
                st.error(f"Błąd: {extract_db_error(exc)}")


with tab_types:
    st.subheader("Lista typów biletów")
    st.caption(
        "Zmiana ceny istniejącego typu uruchomi trigger `trg_PriceHistoryAudit`, "
        "który automatycznie zapisze wpis w `PriceHistory`."
    )
    types_all = type_repo.list_all()
    confs_for_select = conf_repo.list_all()
    conf_by_id = {c.conference_id: c for c in confs_for_select}

    if types_all:
        df = pd.DataFrame([{
            "ID": tt.ticket_type_id,
            "Konferencja": conf_by_id[tt.conference_id].name if tt.conference_id in conf_by_id else f"ID {tt.conference_id}",
            "Nazwa": tt.name,
            "Cena": f"{tt.price:.2f}",
            "Max": tt.max_quantity,
            "Sprzedaż od": tt.sales_start,
            "Sprzedaż do": tt.sales_end,
        } for tt in types_all])
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("Brak typów biletów w bazie.")

    st.divider()

    st.subheader("Dodaj nowy typ biletu")
    if not confs_for_select:
        st.warning("Najpierw musi istnieć przynajmniej jedna konferencja.")
    else:
        with st.form("add_type_form", clear_on_submit=True):
            conf_options = {f"{c.name}": c.conference_id for c in confs_for_select}
            tt_conf_label = st.selectbox("Konferencja *", list(conf_options.keys()), key="add_type_conf")
            tt_conf_id = conf_options[tt_conf_label]
            c1, c2 = st.columns(2)
            with c1:
                tt_name = st.text_input("Nazwa typu *")
                tt_price = st.number_input("Cena (PLN) *", min_value=0.0, value=100.0, step=10.0, format="%.2f")
                tt_sales_start = st.date_input("Sprzedaż od *", value=date.today())
            with c2:
                tt_max = st.number_input("Max ilość *", min_value=1, value=100, step=10)
                tt_sales_end = st.date_input("Sprzedaż do *", value=date.today())
            if st.form_submit_button("Dodaj typ biletu", type="primary"):
                if not tt_name:
                    st.error("Nazwa typu jest wymagana.")
                elif tt_sales_end < tt_sales_start:
                    st.error("Data końca sprzedaży nie może być wcześniejsza niż początek.")
                else:
                    try:
                        new_id = type_repo.create(tt_conf_id, tt_name, Decimal(str(tt_price)),
                                                  int(tt_max), tt_sales_start, tt_sales_end)
                        st.success(f"Typ biletu dodany. TicketTypeID: **{new_id}**")
                        st.rerun()
                    except Exception as exc:
                        st.error(f"Błąd: {extract_db_error(exc)}")

    st.divider()

    st.subheader("Edytuj / usuń typ biletu")
    if types_all and confs_for_select:
        edit_options = {
            f"#{tt.ticket_type_id} {tt.name} ({conf_by_id[tt.conference_id].name if tt.conference_id in conf_by_id else 'ID ' + str(tt.conference_id)}) — {tt.price:.2f} PLN": tt
            for tt in types_all
        }
        sel_label = st.selectbox("Wybierz typ biletu", list(edit_options.keys()), key="edit_type_sel")
        sel_tt = edit_options[sel_label]

        with st.form("edit_type_form"):
            conf_options = {f"{c.name}": c.conference_id for c in confs_for_select}
            current_conf_label = next((k for k, v in conf_options.items() if v == sel_tt.conference_id), list(conf_options.keys())[0])
            e_conf_label = st.selectbox("Konferencja", list(conf_options.keys()),
                                         index=list(conf_options.keys()).index(current_conf_label),
                                         key="edit_type_conf")
            e_conf_id = conf_options[e_conf_label]
            c1, c2 = st.columns(2)
            with c1:
                e_name = st.text_input("Nazwa typu", value=sel_tt.name)
                e_price = st.number_input("Cena (PLN)", min_value=0.0,
                                          value=float(sel_tt.price), step=10.0, format="%.2f")
                e_sales_start = st.date_input("Sprzedaż od", value=sel_tt.sales_start)
            with c2:
                e_max = st.number_input("Max ilość", min_value=1, value=sel_tt.max_quantity, step=10)
                e_sales_end = st.date_input("Sprzedaż do", value=sel_tt.sales_end)
            if st.form_submit_button("Zapisz zmiany", type="primary"):
                if e_sales_end < e_sales_start:
                    st.error("Data końca sprzedaży nie może być wcześniejsza niż początek.")
                else:
                    try:
                        type_repo.update(sel_tt.ticket_type_id, e_conf_id, e_name,
                                         Decimal(str(e_price)), int(e_max),
                                         e_sales_start, e_sales_end)
                        st.success("Zmiany zapisane. Jeśli zmieniono cenę — trigger zapisał wpis w `PriceHistory`.")
                        st.rerun()
                    except Exception as exc:
                        st.error(f"Błąd: {extract_db_error(exc)}")

        confirm_del = st.checkbox("Tak, na pewno chcę usunąć ten typ biletu", key=f"confirm_del_type_{sel_tt.ticket_type_id}")
        if st.button("Usuń typ biletu", type="secondary", disabled=not confirm_del, key=f"del_type_{sel_tt.ticket_type_id}"):
            try:
                type_repo.delete(sel_tt.ticket_type_id)
                st.success(f"Typ biletu #{sel_tt.ticket_type_id} usunięty.")
                st.rerun()
            except Exception as exc:
                st.error(f"Błąd: {extract_db_error(exc)} (typ biletu prawdopodobnie ma już sprzedane bilety).")


with tab_sessions:
    st.subheader("Lista sesji")
    sessions = sess_repo.list_all()
    confs_for_select = conf_repo.list_all()
    rooms_for_select = room_repo.list_all()
    speakers_for_select = speaker_repo.list_all()
    tracks_for_select = track_repo.list_all()

    conf_by_id = {c.conference_id: c for c in confs_for_select}
    room_by_id = {r.room_id: r for r in rooms_for_select}
    speaker_by_id = {s.speaker_id: s for s in speakers_for_select}
    track_by_id = {t.track_id: t for t in tracks_for_select}

    if sessions:
        df = pd.DataFrame([{
            "ID": s.session_id,
            "Konferencja": conf_by_id[s.conference_id].name if s.conference_id in conf_by_id else f"ID {s.conference_id}",
            "Tytuł": s.title,
            "Ścieżka": track_by_id[s.track_id].name if (s.track_id and s.track_id in track_by_id) else "—",
            "Sala": room_by_id[s.room_id].name if s.room_id in room_by_id else f"ID {s.room_id}",
            "Prelegent": speaker_by_id[s.speaker_id].full_name if s.speaker_id in speaker_by_id else f"ID {s.speaker_id}",
            "Start": s.start_time.strftime("%Y-%m-%d %H:%M"),
            "Koniec": s.end_time.strftime("%Y-%m-%d %H:%M"),
            "Typ": s.session_type,
            "Poziom": s.difficulty_level,
        } for s in sessions])
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("Brak sesji w bazie.")

    st.divider()

    st.subheader("Dodaj nową sesję")
    if not (confs_for_select and rooms_for_select and speakers_for_select):
        st.warning("Najpierw musi istnieć przynajmniej jedna konferencja, sala i prelegent.")
    else:
        new_conf_options = {f"{c.name}": c.conference_id for c in confs_for_select}
        new_conf_label = st.selectbox("Konferencja *", list(new_conf_options.keys()), key="add_sess_conf")
        new_conf_id = new_conf_options[new_conf_label]

        tracks_in_conf = [t for t in tracks_for_select if t.conference_id == new_conf_id]
        track_choices = {"(brak ścieżki)": None}
        for t in tracks_in_conf:
            track_choices[t.name] = t.track_id

        with st.form("add_session_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                se_title = st.text_input("Tytuł sesji *")
                se_track_label = st.selectbox("Ścieżka tematyczna", list(track_choices.keys()), key="add_sess_track")
                se_track_id = track_choices[se_track_label]
                room_options = {f"{r.name} (cap {r.capacity})": r.room_id for r in rooms_for_select}
                se_room_label = st.selectbox("Sala *", list(room_options.keys()), key="add_sess_room")
                se_room_id = room_options[se_room_label]
                speaker_options = {f"{s.full_name} ({s.email})": s.speaker_id for s in speakers_for_select}
                se_speaker_label = st.selectbox("Prelegent *", list(speaker_options.keys()), key="add_sess_speaker")
                se_speaker_id = speaker_options[se_speaker_label]
            with c2:
                se_start_date = st.date_input("Data rozpoczęcia *", value=date.today())
                se_start_time = st.time_input("Godzina rozpoczęcia *", value=time(9, 0))
                se_end_date = st.date_input("Data zakończenia *", value=date.today())
                se_end_time = st.time_input("Godzina zakończenia *", value=time(10, 0))
                se_type = st.radio("Typ sesji *", ["Talk", "Workshop"], horizontal=True)
                se_difficulty = st.selectbox("Poziom *", ["Beginner", "Intermediate", "Advanced", "Expert"])

            if st.form_submit_button("Dodaj sesję", type="primary"):
                start_dt = datetime.combine(se_start_date, se_start_time)
                end_dt = datetime.combine(se_end_date, se_end_time)
                if not se_title:
                    st.error("Tytuł sesji jest wymagany.")
                elif end_dt <= start_dt:
                    st.error("Czas zakończenia musi być późniejszy niż czas rozpoczęcia.")
                else:
                    try:
                        new_id = sess_repo.create(new_conf_id, se_track_id, se_room_id,
                                                   se_speaker_id, se_title, start_dt, end_dt,
                                                   se_type, se_difficulty)
                        st.success(f"Sesja dodana. SessionID: **{new_id}**")
                        st.rerun()
                    except Exception as exc:
                        st.error(f"Błąd: {extract_db_error(exc)}")

    st.divider()

    st.subheader("Edytuj / usuń sesję")
    if sessions and confs_for_select and rooms_for_select and speakers_for_select:
        edit_options = {
            f"#{s.session_id} {s.title} ({s.start_time:%Y-%m-%d %H:%M})": s
            for s in sessions
        }
        sel_label = st.selectbox("Wybierz sesję", list(edit_options.keys()), key="edit_sess_sel")
        sel_s = edit_options[sel_label]

        conf_options_e = {f"{c.name}": c.conference_id for c in confs_for_select}
        current_conf_label_e = next((k for k, v in conf_options_e.items() if v == sel_s.conference_id), list(conf_options_e.keys())[0])
        e_conf_label = st.selectbox("Konferencja", list(conf_options_e.keys()),
                                     index=list(conf_options_e.keys()).index(current_conf_label_e),
                                     key="edit_sess_conf")
        e_conf_id = conf_options_e[e_conf_label]

        tracks_in_conf_e = [t for t in tracks_for_select if t.conference_id == e_conf_id]
        track_choices_e = {"(brak ścieżki)": None}
        for t in tracks_in_conf_e:
            track_choices_e[t.name] = t.track_id

        current_track_label_e = next(
            (k for k, v in track_choices_e.items() if v == sel_s.track_id),
            "(brak ścieżki)",
        )

        with st.form("edit_session_form"):
            c1, c2 = st.columns(2)
            with c1:
                e_title = st.text_input("Tytuł", value=sel_s.title)
                e_track_label = st.selectbox("Ścieżka tematyczna",
                                              list(track_choices_e.keys()),
                                              index=list(track_choices_e.keys()).index(current_track_label_e),
                                              key="edit_sess_track")
                e_track_id = track_choices_e[e_track_label]

                room_options_e = {f"{r.name} (cap {r.capacity})": r.room_id for r in rooms_for_select}
                current_room_label_e = next((k for k, v in room_options_e.items() if v == sel_s.room_id), list(room_options_e.keys())[0])
                e_room_label = st.selectbox("Sala", list(room_options_e.keys()),
                                             index=list(room_options_e.keys()).index(current_room_label_e),
                                             key="edit_sess_room")
                e_room_id = room_options_e[e_room_label]

                speaker_options_e = {f"{s.full_name} ({s.email})": s.speaker_id for s in speakers_for_select}
                current_speaker_label_e = next((k for k, v in speaker_options_e.items() if v == sel_s.speaker_id), list(speaker_options_e.keys())[0])
                e_speaker_label = st.selectbox("Prelegent", list(speaker_options_e.keys()),
                                                index=list(speaker_options_e.keys()).index(current_speaker_label_e),
                                                key="edit_sess_speaker")
                e_speaker_id = speaker_options_e[e_speaker_label]

            with c2:
                e_start_date = st.date_input("Data rozpoczęcia", value=sel_s.start_time.date())
                e_start_time = st.time_input("Godzina rozpoczęcia", value=sel_s.start_time.time())
                e_end_date = st.date_input("Data zakończenia", value=sel_s.end_time.date())
                e_end_time = st.time_input("Godzina zakończenia", value=sel_s.end_time.time())
                e_type = st.radio("Typ sesji", ["Talk", "Workshop"],
                                  index=["Talk", "Workshop"].index(sel_s.session_type),
                                  horizontal=True, key="edit_sess_type")
                difficulties = ["Beginner", "Intermediate", "Advanced", "Expert"]
                e_difficulty = st.selectbox("Poziom", difficulties,
                                             index=difficulties.index(sel_s.difficulty_level),
                                             key="edit_sess_diff")

            if st.form_submit_button("Zapisz zmiany", type="primary"):
                start_dt = datetime.combine(e_start_date, e_start_time)
                end_dt = datetime.combine(e_end_date, e_end_time)
                if end_dt <= start_dt:
                    st.error("Czas zakończenia musi być późniejszy niż czas rozpoczęcia.")
                else:
                    try:
                        sess_repo.update(sel_s.session_id, e_conf_id, e_track_id, e_room_id,
                                         e_speaker_id, e_title, start_dt, end_dt,
                                         e_type, e_difficulty)
                        st.success("Zmiany zapisane.")
                        st.rerun()
                    except Exception as exc:
                        st.error(f"Błąd: {extract_db_error(exc)}")

        confirm_del = st.checkbox("Tak, na pewno chcę usunąć tę sesję", key=f"confirm_del_sess_{sel_s.session_id}")
        if st.button("Usuń sesję", type="secondary", disabled=not confirm_del, key=f"del_sess_{sel_s.session_id}"):
            try:
                sess_repo.delete(sel_s.session_id)
                st.success(f"Sesja #{sel_s.session_id} usunięta.")
                st.rerun()
            except Exception as exc:
                st.error(f"Błąd: {extract_db_error(exc)} (sesja prawdopodobnie ma zapisy uczestników).")
