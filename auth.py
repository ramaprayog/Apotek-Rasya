import streamlit as st
import psycopg2
from datetime import datetime
from db import get_connection  # pastikan file db.py punya fungsi ini

from datetime import datetime

def login_section():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT user_id, username, role FROM users WHERE username = %s AND password = %s",
            (username, password)
        )
        result = cur.fetchone()

        if result:
            user_id = result[0]
            st.session_state.login = True
            st.session_state.user_id = user_id
            st.session_state.username = result[1]
            st.session_state.role = result[2]

            # ✅ Update last_login di sini
            now = datetime.now()
            cur.execute("UPDATE users SET last_login = %s WHERE user_id = %s", (now, user_id))
            conn.commit()

            st.success("Login berhasil!")
        else:
            st.error("Username atau password salah.")

        cur.close()
        conn.close()


def signup_section():
    st.title("Sign Up")
    nama = st.text_input("Nama Lengkap")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    role = st.selectbox("Daftar sebagai", ["apoteker", "pelanggan"])

    # Input identitas khusus per role
    nip = nik = None
    if role == "apoteker":
        nip = st.text_input("NIP Apoteker")
    elif role == "pelanggan":
        nik = st.text_input("NIK Pelanggan")

    if st.button("Daftar"):
        conn = get_connection()
        cur = conn.cursor()

        try:
            # Simpan user utama
            cur.execute(
                "INSERT INTO users (username, password, role, nama) VALUES (%s, %s, %s, %s) RETURNING user_id",
                (username, password, role, nama)
            )
            user_id = cur.fetchone()[0]

            # Simpan ke tabel role masing-masing
            if role == "apoteker":
                if not nip:
                    st.error("NIP wajib diisi untuk apoteker.")
                    return
                cur.execute("INSERT INTO apoteker (user_id, nama, nip) VALUES (%s, %s, %s)", (user_id, nama, nip))

            elif role == "pelanggan":
                if not nik:
                    st.error("NIK wajib diisi untuk pelanggan.")
                    return
                cur.execute("INSERT INTO pelanggan (user_id, nama, nik) VALUES (%s, %s, %s)", (user_id, nama, nik))

            conn.commit()
            st.success("Akun berhasil dibuat. Silakan login.")
        except Exception as e:
            conn.rollback()
            st.error(f"Gagal mendaftar: {e}")
        finally:
            cur.close()
            conn.close()