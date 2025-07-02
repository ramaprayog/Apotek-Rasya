import streamlit as st
from auth import login_section, signup_section
import modules.obat as obat
import modules.pelanggan as pelanggan
import modules.apoteker as apoteker
import modules.transaksi as transaksi

# Konfigurasi halaman
st.set_page_config(page_title="Sistem Apotek", layout="wide")

# Inisialisasi session state login
if "login" not in st.session_state:
    st.session_state.login = False

# Jika belum login, tampilkan form login/sign up
if not st.session_state.get("login", False):
    menu = st.sidebar.selectbox("Menu", ["Login", "Sign Up"])
    if menu == "Login":
        login_section()
    else:
        signup_section()

# Jika sudah login
if st.session_state.get("login", False):
    st.sidebar.success(f"Login sebagai {st.session_state.get('username')} ({st.session_state.get('role')})")

    # Tombol Logout
    if st.sidebar.button("Logout"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
    # Menu berdasarkan role
    role = st.session_state.get("role")
    if role == "apoteker":
        pages = ["Obat", "Pelanggan", "Apoteker", "Transaksi"]
    elif role == "pelanggan":
        pages = ["Transaksi"]
    else:
        pages = []

    choice = st.sidebar.selectbox("Halaman", pages)

    # Routing halaman
    if choice == "Obat":
        obat.run()
    elif choice == "Pelanggan":
        pelanggan.run()
    elif choice == "Apoteker":
        apoteker.run()
    elif choice == "Transaksi":
        transaksi.run()