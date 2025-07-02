import streamlit as st
from db import get_connection

def run():
    st.title("Data Obat")

    conn = get_connection()
    cur = conn.cursor()

    # --- Create Obat ---
    st.subheader("Tambah Obat")
    kode = st.text_input("Kode Obat")
    nama = st.text_input("Nama Obat")
    harga = st.number_input("Harga", step=100.0)
    stok = st.number_input("Stok", step=1)
    apoteker_id = st.number_input("ID Apoteker", step=1)
    if st.button("Simpan Obat"):
     if kode and nama and apoteker_id:
        try:
            cur.execute("""
                INSERT INTO obat (kode_obat, nama_obat, harga, stok, apoteker_id)
                VALUES (%s, %s, %s, %s, %s)
            """, (kode, nama, harga, stok, apoteker_id))
            conn.commit()
            st.success("Obat berhasil ditambahkan.")
        except Exception as e:
            conn.rollback()
            st.error(f"Terjadi error saat menyimpan obat: {e}")
    else:
        st.warning("Mohon isi semua kolom dengan benar.")

    # --- Read Obat ---
    st.subheader("Tabel Obat")
    cur.execute("SELECT * FROM obat ORDER BY obat_id")
    rows = cur.fetchall()
    st.dataframe(rows, use_container_width=True)

    # --- Update Obat ---
    st.subheader("Update Obat")
    id_update = st.number_input("Obat ID yang ingin diubah", step=1)
    new_stok = st.number_input("Stok Baru", step=1)
    if st.button("Update Stok"):
        cur.execute("UPDATE obat SET stok = %s WHERE obat_id = %s", (new_stok, id_update))
        conn.commit()
        st.success("Stok berhasil diperbarui.")

    # --- Delete Obat ---
    st.subheader("Hapus Obat")
    id_delete = st.number_input("Obat ID yang ingin dihapus", step=1)
    if st.button("Hapus Obat"):
        cur.execute("DELETE FROM obat WHERE obat_id = %s", (id_delete,))
        conn.commit()
        st.warning("Obat berhasil dihapus.")

    cur.close(); conn.close()