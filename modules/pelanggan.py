import streamlit as st
from db import get_connection

def run():
    st.title("Data Pelanggan")
    conn = get_connection()
    cur = conn.cursor()

    # --- Create Pelanggan ---
    st.subheader("Tambah Pelanggan")
    user_id = st.number_input("User ID", step=1)
    nik = st.text_input("NIK")
    alamat = st.text_area("Alamat")
    if st.button("Simpan Pelanggan"):
        cur.execute("""
            INSERT INTO pelanggan (user_id, nik, alamat)
            VALUES (%s, %s, %s)
        """, (user_id, nik, alamat))
        conn.commit()
        st.success("Pelanggan berhasil ditambahkan.")

    # --- Read Pelanggan ---
    st.subheader("Tabel Pelanggan")
    cur.execute("""
        SELECT p.pelanggan_id, u.username, p.nik, p.alamat
        FROM pelanggan p JOIN users u ON p.user_id = u.user_id
    """)
    rows = cur.fetchall()
    st.dataframe(rows, use_container_width=True)

    # --- Update Pelanggan ---
    st.subheader("Update Alamat")
    pelanggan_id = st.number_input("Pelanggan ID", step=1)
    new_alamat = st.text_area("Alamat Baru")
    if st.button("Update Alamat"):
        cur.execute("UPDATE pelanggan SET alamat = %s WHERE pelanggan_id = %s", (new_alamat, pelanggan_id))
        conn.commit()
        st.success("Alamat berhasil diubah.")

    # --- Delete Pelanggan ---
    st.subheader("Hapus Pelanggan")
    id_delete = st.number_input("ID Pelanggan yang ingin dihapus", step=1)
    if st.button("Hapus"):
        cur.execute("DELETE FROM pelanggan WHERE pelanggan_id = %s", (id_delete,))
        conn.commit()
        st.warning("Pelanggan berhasil dihapus.")

    cur.close(); conn.close()