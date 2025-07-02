import streamlit as st
from db import get_connection

def run():
    st.title("Data Apoteker")
    conn = get_connection()
    cur = conn.cursor()

    # --- Create Apoteker ---
    st.subheader("Tambah Apoteker")
    user_id = st.number_input("User ID", step=1)
    nip = st.text_input("NIP")
    if st.button("Simpan Apoteker"):
        cur.execute("INSERT INTO apoteker (user_id, nip) VALUES (%s, %s)", (user_id, nip))
        conn.commit()
        st.success("Apoteker berhasil ditambahkan.")

    # --- Read Apoteker ---
    st.subheader("Tabel Apoteker")
    cur.execute("""
        SELECT a.apoteker_id, u.username, a.nip
        FROM apoteker a JOIN users u ON a.user_id = u.user_id
    """)
    rows = cur.fetchall()
    st.dataframe(rows, use_container_width=True)

    # --- Update NIP ---
    st.subheader("Update NIP")
    apoteker_id = st.number_input("ID Apoteker", step=1,
    key="update_apoteker")
    new_nip = st.text_input("NIP Baru")
    if st.button("Update NIP"):
        cur.execute("UPDATE apoteker SET nip = %s WHERE apoteker_id = %s", (new_nip, apoteker_id))
        conn.commit()
        st.success("NIP berhasil diubah.")

    # --- Delete Apoteker ---
    st.subheader("Hapus Apoteker")
    id_delete = st.number_input("ID Apoteker", step=1,
    key="delete_apoteker")
    if st.button("Hapus Apoteker"):
        cur.execute("DELETE FROM apoteker WHERE apoteker_id = %s", (id_delete,))
        conn.commit()
        st.warning("Apoteker berhasil dihapus.")

    cur.close(); conn.close()