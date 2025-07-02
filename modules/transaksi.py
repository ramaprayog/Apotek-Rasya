import streamlit as st
import pandas as pd
import altair as alt
from db import get_connection

def run():
    st.title("Data Transaksi")
    conn = get_connection()
    cur = conn.cursor()

    # ================== ROLE: PELANGGAN ==================
    if st.session_state.get("role") == "pelanggan":
        st.info("Anda hanya dapat melihat transaksi Anda sendiri.")

        cur.execute("SELECT pelanggan_id FROM pelanggan WHERE user_id = %s", (st.session_state.user_id,))
        result = cur.fetchone()
        if not result:
            st.error("Data pelanggan tidak ditemukan.")
            return
        pelanggan_id = result[0]

        cur.execute("""
            SELECT t.transaksi_id, o.nama_obat, t.jumlah, t.total_harga, t.tanggal
            FROM transaksi t
            JOIN obat o ON t.obat_id = o.obat_id
            WHERE t.pelanggan_id = %s
        """, (pelanggan_id,))
        df = pd.DataFrame(cur.fetchall(), columns=["ID", "Obat", "Jumlah", "Total", "Tanggal"])
        st.dataframe(df, use_container_width=True)

        if not df.empty:
            st.subheader("📊 Obat Terbanyak Anda")
            chart_data = df.groupby("Obat")["Jumlah"].sum().reset_index()
            st.altair_chart(alt.Chart(chart_data).mark_bar().encode(x='Obat', y='Jumlah'), use_container_width=True)

            st.subheader("📈 Total Pembelian Harian Anda")
            line_data = df.groupby("Tanggal")["Total"].sum().reset_index()
            st.altair_chart(alt.Chart(line_data).mark_line(point=True).encode(x='Tanggal:T', y='Total:Q'), use_container_width=True)

        cur.close()
        conn.close()
        return

    # ================== ROLE: APOTEKER ==================
    if st.session_state.get("role") == "apoteker":
        st.subheader("➕ Tambah Transaksi")
        try:
            # Pilih Pelanggan
            cur.execute("SELECT pelanggan_id, nama FROM pelanggan")
            pelanggan_list = cur.fetchall()
            selected_pelanggan = st.selectbox("Pilih Pelanggan", pelanggan_list, format_func=lambda x: f"{x[0]} - {x[1]}")
            pelanggan_id = selected_pelanggan[0]

            # Pilih Obat
            cur.execute("SELECT obat_id, nama_obat, harga, stok FROM obat")
            obat_list = cur.fetchall()
            obat_dict = {f"{nama_obat} (ID {oid}) - Stok: {stok}": (oid, harga, stok) for oid, nama_obat, harga, stok in obat_list}
            selected_label = st.selectbox("Pilih Obat", list(obat_dict.keys()))
            obat_id, harga_satuan, stok_tersedia = obat_dict[selected_label]

            jumlah = st.number_input("Jumlah", min_value=1, step=1)
            total = jumlah * harga_satuan
            st.write(f"Total Harga: Rp {total:,.0f}")

            if jumlah > stok_tersedia:
                st.error(f"Stok tidak cukup. Tersisa: {stok_tersedia}")
            elif st.button("Simpan Transaksi"):
                try:
                    cur.execute("""
                        INSERT INTO transaksi (pelanggan_id, obat_id, jumlah, total_harga)
                        VALUES (%s, %s, %s, %s)
                    """, (pelanggan_id, obat_id, jumlah, total))

                    cur.execute("UPDATE obat SET stok = stok - %s WHERE obat_id = %s", (jumlah, obat_id))
                    conn.commit()
                    st.success("Transaksi berhasil disimpan dan stok diperbarui.")
                except Exception as e:
                    conn.rollback()
                    st.error(f"Error saat menyimpan transaksi: {e}")
        except Exception as e:
            st.error(f"Gagal load data: {e}")

        # ================== UPDATE TRANSAKSI ==================
        st.subheader("✏️ Update Jumlah Transaksi")
        id_trans = st.number_input("ID Transaksi", step=1, format="%d", key="update_id")
        new_jumlah = st.number_input("Jumlah Baru", min_value=1, step=1, key="update_jumlah")

        if st.button("Update Transaksi"):
            try:
                cur.execute("""
                    SELECT t.jumlah, o.harga, t.obat_id, o.stok
                    FROM transaksi t
                    JOIN obat o ON t.obat_id = o.obat_id
                    WHERE t.transaksi_id = %s
                """, (id_trans,))
                result = cur.fetchone()

                if result:
                    jumlah_lama, harga_satuan, obat_id, stok_now = result
                    selisih = new_jumlah - jumlah_lama
                    total_baru = new_jumlah * harga_satuan

                    # Cek stok jika butuh tambahan
                    if selisih > 0 and stok_now < selisih:
                        st.error(f"Stok tidak cukup untuk menambah {selisih} item. Stok tersisa: {stok_now}")
                    else:
                        cur.execute("""
                            UPDATE transaksi
                            SET jumlah = %s, total_harga = %s
                            WHERE transaksi_id = %s
                        """, (new_jumlah, total_baru, id_trans))

                        cur.execute("UPDATE obat SET stok = stok - %s WHERE obat_id = %s", (selisih, obat_id))
                        conn.commit()
                        st.success("Transaksi dan stok berhasil diperbarui.")
                else:
                    st.warning("ID transaksi tidak ditemukan.")
            except Exception as e:
                conn.rollback()
                st.error(f"Error saat update: {e}")

        # ================== DELETE TRANSAKSI ==================
        st.subheader("🗑️ Hapus Transaksi")
        id_hapus = st.number_input("ID Transaksi yang ingin dihapus", step=1, format="%d", key="delete_id")

        if st.button("Hapus Transaksi"):
            try:
                # Tambahkan pengembalian stok jika perlu (opsional)
                cur.execute("""
                    SELECT jumlah, obat_id FROM transaksi WHERE transaksi_id = %s
                """, (id_hapus,))
                hasil = cur.fetchone()

                if hasil:
                    jumlah_hapus, obat_id = hasil
                    cur.execute("DELETE FROM transaksi WHERE transaksi_id = %s", (id_hapus,))
                    cur.execute("UPDATE obat SET stok = stok + %s WHERE obat_id = %s", (jumlah_hapus, obat_id))
                    conn.commit()
                    st.warning("Transaksi berhasil dihapus dan stok dikembalikan.")
                else:
                    st.warning("ID transaksi tidak ditemukan.")
            except Exception as e:
                conn.rollback()
                st.error(f"Gagal menghapus transaksi: {e}")

    # ================== TAMPILKAN SEMUA TRANSAKSI ==================
    st.subheader("📋 Tabel Semua Transaksi")
    cur.execute("""
        SELECT t.transaksi_id, u.nama, o.nama_obat, t.jumlah, t.total_harga, t.tanggal
        FROM transaksi t
        JOIN pelanggan p ON t.pelanggan_id = p.pelanggan_id
        JOIN users u ON p.user_id = u.user_id
        JOIN obat o ON t.obat_id = o.obat_id
    """)
    rows = cur.fetchall()
    df = pd.DataFrame(rows, columns=["ID", "Pelanggan", "Obat", "Jumlah", "Total", "Tanggal"])
    st.dataframe(df, use_container_width=True)

    if not df.empty:
        st.subheader("📊 Obat Terlaris")
        chart_data = df.groupby("Obat")["Jumlah"].sum().reset_index()
        st.altair_chart(alt.Chart(chart_data).mark_bar().encode(x='Obat', y='Jumlah'), use_container_width=True)

        st.subheader("📈 Total Transaksi Harian")
        line_data = df.groupby("Tanggal")["Total"].sum().reset_index()
        st.altair_chart(alt.Chart(line_data).mark_line(point=True).encode(x='Tanggal:T', y='Total:Q'), use_container_width=True)

    cur.close()
    conn.close()