import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pyodbc
import bcrypt
import pandas as pd

# --- KONFIGURASI KONEKSI DATABASE ---
SERVER = r'' # input your server
DB_PROJECT = r'CRYPTO_PROJECT'  # input your database for Crypto. Mine is CRYPTO_PROJECT (Make sure you create first using Microsoft SQL Server Management Studio)
DB_ADMIN = r'Admin_DB'          # input your database for admin. Mine is Admin_DB (Make sure you create first using Microsoft SQL Server Management Studio)
# USERNAME = 'sa' # change with your username
# PASSWORD = 'PasswordAnda123' # change with your password

# --- KELAS UNTUK JENDELA LOGIN (Tidak ada perubahan signifikan) ---
class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Login Aplikasi")
        self.root.geometry("350x180")
        self.root.resizable(False, False)
        
        self.login_successful = False

        frame = ttk.Frame(root, padding="20")
        frame.pack(expand=True, fill="both")

        ttk.Label(frame, text="Username:").grid(row=0, column=0, sticky="w", pady=5)
        self.user_entry = ttk.Entry(frame, width=30)
        self.user_entry.grid(row=0, column=1, pady=5)

        ttk.Label(frame, text="Password:").grid(row=1, column=0, sticky="w", pady=5)
        self.pass_entry = ttk.Entry(frame, width=30, show="*")
        self.pass_entry.grid(row=1, column=1, pady=5)

        login_button = ttk.Button(frame, text="Login", command=self.check_login)
        login_button.grid(row=2, column=0, columnspan=2, pady=15)
        
        self.user_entry.focus_set()
        self.root.bind('<Return>', lambda event=None: login_button.invoke())

    def get_connection(self, db_name):
        try:
            conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={SERVER};DATABASE={db_name};Trusted_Connection=yes;'
            # Jika pakai SQL Server Authentication (username & password)
            # conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD};'
            conn = pyodbc.connect(conn_str)
            return conn
        except pyodbc.Error as ex:
            messagebox.showerror("Koneksi Gagal", f"Gagal terhubung ke database:\n{ex}")
            return None

    def check_login(self):
        username = self.user_entry.get()
        password = self.pass_entry.get().encode('utf-8')

        if not username or not password:
            messagebox.showerror("Login Gagal", "Username dan Password tidak boleh kosong.")
            return

        conn = self.get_connection(DB_ADMIN)
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute("SELECT PasswordHash FROM Users WHERE Username=?", username)
                row = cursor.fetchone()
            except pyodbc.ProgrammingError:
                messagebox.showerror("Struktur DB Salah", f"Tabel 'Users' atau kolom 'PasswordHash'/'Username' tidak ditemukan di database '{DB_ADMIN}'.")
                row = None
            finally:
                cursor.close()
                conn.close()

            if row:
                stored_hash = row.PasswordHash.encode('utf-8')
                if bcrypt.checkpw(password, stored_hash):
                    messagebox.showinfo("Login Berhasil", f"Selamat datang, {username}!")
                    self.login_successful = True
                    self.root.destroy()
                else:
                    messagebox.showerror("Login Gagal", "Username atau Password salah.")
            else:
                messagebox.showerror("Login Gagal", "Username atau Password salah.")

# --- KELAS UTAMA APLIKASI (PERUBAHAN DI FUNGSI TAMBAH) ---
class AplikasiProject:
    # __init__ dan fungsi lainnya tetap sama seperti sebelumnya
    def __init__(self, root):
        self.root = root
        self.root.title("Aplikasi Manajemen Proyek Kripto")
        self.root.geometry("1600x700")
        self.user_logged_out = False
        self.frame_tombol = ttk.LabelFrame(root, text="Menu Aksi")
        self.frame_tombol.pack(pady=10, padx=10, fill="x")
        ttk.Button(self.frame_tombol, text="Tambah Proyek Baru...", command=self.buka_dialog_tambah).pack(side="left", padx=10, pady=5)
        ttk.Button(self.frame_tombol, text="Update Data Proyek...", command=self.buka_dialog_update).pack(side="left", padx=10, pady=5)
        ttk.Button(self.frame_tombol, text="Hapus Data Proyek...", command=self.buka_dialog_hapus).pack(side="left", padx=10, pady=5)
        style = ttk.Style()
        style.configure("logout.TButton", foreground="blue")
        ttk.Button(self.frame_tombol, text="Logout", command=self.logout, style="logout.TButton").pack(side="right", padx=10, pady=5)
        self.frame_filter = ttk.LabelFrame(root, text="Pencarian dan Filter")
        self.frame_filter.pack(pady=5, padx=10, fill="x")
        ttk.Label(self.frame_filter, text="Cari Nama Proyek:").pack(side="left", padx=(10, 5), pady=5)
        self.search_entry = ttk.Entry(self.frame_filter, width=30)
        self.search_entry.pack(side="left", padx=5, pady=5)
        ttk.Button(self.frame_filter, text="Cari", command=self.cari_project).pack(side="left", padx=5, pady=5)
        ttk.Button(self.frame_filter, text="Tampilkan Semua", command=self.tampilkan_semua).pack(side="left", padx=5, pady=5)
        self.frame_sort = ttk.LabelFrame(root, text="Pengurutan dan Ekspor")
        self.frame_sort.pack(pady=5, padx=10, fill="x")
        ttk.Button(self.frame_sort, text="Urutkan Nama A-Z", command=self.urutkan_nama_az).pack(side="left", padx=(10, 5), pady=5)
        ttk.Button(self.frame_sort, text="Urutkan Nama Z-A", command=self.urutkan_nama_za).pack(side="left", padx=5, pady=5)
        ttk.Button(self.frame_sort, text="Urutkan ID ↑", command=self.urutkan_id_asc).pack(side="left", padx=(15, 5), pady=5)
        ttk.Button(self.frame_sort, text="Urutkan ID ↓", command=self.urutkan_id_desc).pack(side="left", padx=5, pady=5)
        style.configure("export.TButton", foreground="green")
        ttk.Button(self.frame_sort, text="Ekspor ke Excel", command=self.ekspor_ke_excel, style="export.TButton").pack(side="right", padx=10, pady=5)
        self.frame_tabel = ttk.LabelFrame(root, text="Data Proyek Kripto")
        self.frame_tabel.pack(pady=10, padx=10, fill="both", expand=True)
        kolom = ("ID", "NamaProject", "KapanMulai", "Jaringan", "Fase", "Status", "InfoTGE", "InfoListing", "Misi", "LinkGarapan", "KodeReferal")
        self.tree = ttk.Treeview(self.frame_tabel, columns=kolom, show="headings")
        self.tree.heading("ID", text="ID"); self.tree.column("ID", width=40, anchor="center")
        self.tree.heading("NamaProject", text="Nama Proyek"); self.tree.column("NamaProject", width=200)
        self.tree.heading("KapanMulai", text="Mulai"); self.tree.column("KapanMulai", width=120)
        self.tree.heading("Jaringan", text="Jaringan"); self.tree.column("Jaringan", width=120)
        self.tree.heading("Fase", text="Fase"); self.tree.column("Fase", width=80, anchor="center")
        self.tree.heading("Status", text="Status"); self.tree.column("Status", width=100)
        self.tree.heading("InfoTGE", text="Info TGE"); self.tree.column("InfoTGE", width=150)
        self.tree.heading("InfoListing", text="Info Listing"); self.tree.column("InfoListing", width=150)
        self.tree.heading("Misi", text="Misi"); self.tree.column("Misi", width=200)
        self.tree.heading("LinkGarapan", text="Link"); self.tree.column("LinkGarapan", width=200)
        self.tree.heading("KodeReferal", text="Referal"); self.tree.column("KodeReferal", width=100)
        yscrollbar = ttk.Scrollbar(self.frame_tabel, orient="vertical", command=self.tree.yview)
        xscrollbar = ttk.Scrollbar(self.frame_tabel, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=yscrollbar.set, xscrollcommand=xscrollbar.set)
        yscrollbar.pack(side="right", fill="y")
        xscrollbar.pack(side="bottom", fill="x")
        self.tree.pack(side="left", fill="both", expand=True)
        self.muat_ulang_data()
    def get_connection(self, db_name):
        try:
            conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={SERVER};DATABASE={db_name};Trusted_Connection=yes;'
            # Jika pakai SQL Server Authentication (username & password)
            # conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD};'
            conn = pyodbc.connect(conn_str)
            return conn
        except pyodbc.Error as ex:
            messagebox.showerror("Koneksi Gagal", f"Gagal terhubung ke database:\n{ex}")
            return None
    def muat_ulang_data(self, search_term=None, sort_column='ID', sort_direction='ASC'):
        for i in self.tree.get_children(): self.tree.delete(i)
        conn = self.get_connection(DB_PROJECT)
        if conn:
            cursor = conn.cursor()
            params = []
            valid_columns = ['ID', 'NamaProject']
            if sort_column not in valid_columns: sort_column = 'ID'
            sql_query = "SELECT ID, NamaProject, KapanMulai, Jaringan, Fase, Status, InfoTGE, InfoListing, Misi, LinkGarapan, KodeReferal FROM Project"
            if search_term and search_term.strip() != "":
                sql_query += " WHERE NamaProject LIKE ?"
                params.append(f'%{search_term}%')
            sql_query += f" ORDER BY {sort_column} {sort_direction}"
            try:
                cursor.execute(sql_query, tuple(params))
                for row in cursor.fetchall():
                    self.tree.insert("", "end", values=list(row))
            except pyodbc.ProgrammingError as e:
                 messagebox.showerror("Error Query", f"Gagal mengambil data. Pastikan tabel 'Project' dan kolom-kolomnya ada di database '{DB_PROJECT}'.\n\nDetail: {e}")
            finally:
                cursor.close()
                conn.close()

    # <<< FUNGSI INI DIUBAH SECARA SIGNIFIKAN >>>
    def buka_dialog_tambah(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Tambah Proyek Baru")
        dialog.geometry("500x500") # Sedikit diperbesar
        dialog.transient(self.root)
        dialog.grab_set()

        form = ttk.Frame(dialog)
        form.pack(padx=20, pady=20, fill="both", expand=True)

        # Dictionary untuk menampung widget input
        widgets = {}
        row_num = 0

        # --- Field-field input ---
        # NamaProject, KapanMulai, Jaringan (tetap Entry biasa)
        for field in ["NamaProject", "KapanMulai", "Jaringan"]:
            ttk.Label(form, text=f"{field}:").grid(row=row_num, column=0, sticky="w", pady=5)
            entry = ttk.Entry(form, width=50)
            entry.grid(row=row_num, column=1, columnspan=2, pady=5)
            widgets[field] = entry
            row_num += 1

        # 1. Fase (Dropdown)
        ttk.Label(form, text="Fase:").grid(row=row_num, column=0, sticky="w", pady=5)
        fase_combo = ttk.Combobox(form, values=['Testnet', 'Mainnet'], state="readonly", width=47)
        fase_combo.set('Testnet')
        fase_combo.grid(row=row_num, column=1, columnspan=2, pady=5)
        widgets['Fase'] = fase_combo
        row_num += 1

        # 2. Misi (Dropdown dengan opsi custom)
        ttk.Label(form, text="Misi:").grid(row=row_num, column=0, sticky="w", pady=5)
        misi_options = [
            "- Daily Login",
            "- Daily Login, Daily Mission",
            "- Daily Login, Daily Mission, Daily Transaction",
            "- Daily Login, Daily Mission, Daily Transaction, Daily Yapping",
            "(isi sendiri)"
        ]
        misi_combo = ttk.Combobox(form, values=misi_options, state="readonly", width=47)
        misi_combo.grid(row=row_num, column=1, columnspan=2, pady=5)
        widgets['Misi_combo'] = misi_combo
        row_num += 1

        # Entry untuk Misi custom (awalnya non-aktif)
        custom_misi_entry = ttk.Entry(form, width=50, state="disabled")
        custom_misi_entry.grid(row=row_num, column=1, columnspan=2, pady=5)
        widgets['Misi_custom'] = custom_misi_entry
        row_num += 1
        
        # Fungsi untuk mengaktifkan/menonaktifkan entry custom misi
        def on_misi_select(event):
            if misi_combo.get() == "(isi sendiri)":
                custom_misi_entry.config(state="normal")
                custom_misi_entry.focus()
            else:
                custom_misi_entry.delete(0, "end")
                custom_misi_entry.config(state="disabled")
        misi_combo.bind("<<ComboboxSelected>>", on_misi_select)

        # 3. Info TGE (Dropdown Quarter + Entry Tahun)
        ttk.Label(form, text="Info TGE:").grid(row=row_num, column=0, sticky="w", pady=5)
        tge_frame = ttk.Frame(form)
        tge_frame.grid(row=row_num, column=1, columnspan=2, sticky="w")
        tge_q_combo = ttk.Combobox(tge_frame, values=['Q1', 'Q2', 'Q3', 'Q4'], state="readonly", width=10)
        tge_q_combo.pack(side="left", padx=(0, 10))
        tge_year_entry = ttk.Entry(tge_frame, width=35)
        tge_year_entry.pack(side="left")
        widgets['TGE_Q'] = tge_q_combo
        widgets['TGE_Year'] = tge_year_entry
        row_num += 1

        # LinkGarapan dan KodeReferal (tetap Entry biasa)
        for field in ["LinkGarapan", "KodeReferal"]:
            ttk.Label(form, text=f"{field}:").grid(row=row_num, column=0, sticky="w", pady=5)
            entry = ttk.Entry(form, width=50)
            entry.grid(row=row_num, column=1, columnspan=2, pady=5)
            widgets[field] = entry
            row_num += 1
            
        # 4. Status (Dropdown)
        ttk.Label(form, text="Status:").grid(row=row_num, column=0, sticky="w", pady=5)
        status_combo = ttk.Combobox(form, values=['Ongoing', 'Distributed', 'End'], state="readonly", width=47)
        status_combo.set('Ongoing')
        status_combo.grid(row=row_num, column=1, columnspan=2, pady=5)
        widgets['Status'] = status_combo
        row_num += 1
        
        # 5. Info Listing (Dropdown Quarter + Entry Tahun)
        ttk.Label(form, text="Info Listing:").grid(row=row_num, column=0, sticky="w", pady=5)
        listing_frame = ttk.Frame(form)
        listing_frame.grid(row=row_num, column=1, columnspan=2, sticky="w")
        listing_q_combo = ttk.Combobox(listing_frame, values=['Q1', 'Q2', 'Q3', 'Q4'], state="readonly", width=10)
        listing_q_combo.pack(side="left", padx=(0, 10))
        listing_year_entry = ttk.Entry(listing_frame, width=35)
        listing_year_entry.pack(side="left")
        widgets['Listing_Q'] = listing_q_combo
        widgets['Listing_Year'] = listing_year_entry
        row_num += 1


        def do_tambah():
            # --- Mengambil data dari semua widget ---
            data = {}
            # Ambil data dari entry biasa
            for field in ["NamaProject", "KapanMulai", "Jaringan", "LinkGarapan", "KodeReferal"]:
                data[field] = widgets[field].get()
            
            # Ambil data dari widget custom
            data['Fase'] = widgets['Fase'].get()
            
            if widgets['Misi_combo'].get() == "(isi sendiri)":
                data['Misi'] = widgets['Misi_custom'].get()
            else:
                data['Misi'] = widgets['Misi_combo'].get()

            # Gabungkan Info TGE
            tge_q = widgets['TGE_Q'].get()
            tge_y = widgets['TGE_Year'].get()
            data['InfoTGE'] = f"{tge_q} {tge_y}".strip()

            data['Status'] = widgets['Status'].get()

            # Gabungkan Info Listing
            list_q = widgets['Listing_Q'].get()
            list_y = widgets['Listing_Year'].get()
            data['InfoListing'] = f"{list_q} {list_y}".strip()

            # Validasi kolom NOT NULL
            if not data["NamaProject"] or not data["KapanMulai"] or not data["Jaringan"] or not data["Status"]:
                messagebox.showwarning("Input Kosong", "Kolom NamaProject, KapanMulai, Jaringan, dan Status harus diisi.", parent=dialog)
                return

            conn = self.get_connection(DB_PROJECT)
            if conn:
                cursor = conn.cursor()
                sql = """
                    INSERT INTO Project (NamaProject, KapanMulai, Jaringan, Fase, Misi, 
                                       InfoTGE, LinkGarapan, KodeReferal, Status, InfoListing)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                # Urutkan value sesuai urutan kolom di SQL
                values = (data['NamaProject'], data['KapanMulai'], data['Jaringan'], data['Fase'], 
                          data['Misi'], data['InfoTGE'], data['LinkGarapan'], data['KodeReferal'],
                          data['Status'], data['InfoListing'])

                cursor.execute(sql, values)
                conn.commit()
                cursor.close()
                conn.close()
                messagebox.showinfo("Sukses", "Data proyek berhasil ditambahkan.", parent=dialog)
                dialog.destroy()
                self.muat_ulang_data()

        ttk.Button(dialog, text="Simpan Data", command=do_tambah).pack(pady=20)
        widgets["NamaProject"].focus_set()


    # --- Sisa fungsi tidak perlu diubah lagi ---
    def ekspor_ke_excel(self):
        search_term = self.search_entry.get()
        sort_column='ID'
        sort_direction='ASC'
        conn = self.get_connection(DB_PROJECT)
        if not conn: return
        params = []
        sql_query = f"SELECT * FROM Project"
        if search_term and search_term.strip() != "":
            sql_query += " WHERE NamaProject LIKE ?"
            params.append(f'%{search_term}%')
        sql_query += f" ORDER BY {sort_column} {sort_direction}"
        try:
            df = pd.read_sql_query(sql_query, conn, params=tuple(params))
            if df.empty:
                messagebox.showinfo("Informasi", "Tidak ada data untuk diekspor.")
                return
            file_path = filedialog.asksaveasfilename(defaultextension=".xlsx",filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],title="Simpan sebagai file Excel")
            if not file_path: return
            df.to_excel(file_path, index=False)
            messagebox.showinfo("Sukses", f"Data berhasil diekspor ke:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Terjadi kesalahan saat mengekspor data:\n{e}")
        finally:
            conn.close()
    def cari_project(self): self.muat_ulang_data(search_term=self.search_entry.get())
    def tampilkan_semua(self): self.search_entry.delete(0, "end"); self.muat_ulang_data()
    def urutkan_nama_az(self): self.muat_ulang_data(search_term=self.search_entry.get(), sort_column='NamaProject', sort_direction='ASC')
    def urutkan_nama_za(self): self.muat_ulang_data(search_term=self.search_entry.get(), sort_column='NamaProject', sort_direction='DESC')
    def urutkan_id_asc(self): self.muat_ulang_data(search_term=self.search_entry.get(), sort_column='ID', sort_direction='ASC')
    def urutkan_id_desc(self): self.muat_ulang_data(search_term=self.search_entry.get(), sort_column='ID', sort_direction='DESC')
    def logout(self):
        if messagebox.askyesno("Konfirmasi Logout", "Apakah Anda yakin ingin logout?"):
            self.user_logged_out = True
            self.root.destroy()
    def buka_dialog_update(self):
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showinfo("Informasi", "Pilih salah satu proyek dari tabel untuk di-update.")
            return

        project_id = self.tree.item(selected_item, 'values')[0]

        # Ambil data lengkap dari database untuk di-update
        conn_get = self.get_connection(DB_PROJECT)
        if not conn_get: return
        cursor_get = conn_get.cursor()
        try:
            cursor_get.execute("SELECT * FROM Project WHERE ID=?", project_id)
            full_data = cursor_get.fetchone()
        finally:
            cursor_get.close()
            conn_get.close()
        
        if not full_data:
            messagebox.showerror("Error", "Data proyek tidak ditemukan di database.")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title(f"Update Proyek: {full_data.NamaProject}")
        dialog.geometry("500x500")
        dialog.transient(self.root)
        dialog.grab_set()

        form = ttk.Frame(dialog)
        form.pack(padx=20, pady=20, fill="both", expand=True)

        # UI-nya sama persis dengan dialog Tambah
        widgets = {}; row_num = 0
        for field in ["NamaProject", "KapanMulai", "Jaringan"]:
            ttk.Label(form, text=f"{field}:").grid(row=row_num, column=0, sticky="w", pady=5)
            entry = ttk.Entry(form, width=50); entry.grid(row=row_num, column=1, columnspan=2, pady=5)
            widgets[field] = entry; row_num += 1
        ttk.Label(form, text="Fase:").grid(row=row_num, column=0, sticky="w", pady=5)
        fase_combo = ttk.Combobox(form, values=['Testnet', 'Mainnet'], state="readonly", width=47)
        fase_combo.grid(row=row_num, column=1, columnspan=2, pady=5); widgets['Fase'] = fase_combo; row_num += 1
        ttk.Label(form, text="Misi:").grid(row=row_num, column=0, sticky="w", pady=5)
        misi_options = ["- Daily Login", "- Daily Login, Daily Mission", "- Daily Login, Daily Mission, Daily Transaction", "- Daily Login, Daily Mission, Daily Transaction, Daily Yapping", "(isi sendiri)"]
        misi_combo = ttk.Combobox(form, values=misi_options, state="readonly", width=47); misi_combo.grid(row=row_num, column=1, columnspan=2, pady=5)
        widgets['Misi_combo'] = misi_combo; row_num += 1
        custom_misi_entry = ttk.Entry(form, width=50, state="disabled"); custom_misi_entry.grid(row=row_num, column=1, columnspan=2, pady=5)
        widgets['Misi_custom'] = custom_misi_entry; row_num += 1
        def on_misi_select(event):
            if misi_combo.get() == "(isi sendiri)": custom_misi_entry.config(state="normal"); custom_misi_entry.focus()
            else: custom_misi_entry.delete(0, "end"); custom_misi_entry.config(state="disabled")
        misi_combo.bind("<<ComboboxSelected>>", on_misi_select)
        ttk.Label(form, text="Info TGE:").grid(row=row_num, column=0, sticky="w", pady=5)
        tge_frame = ttk.Frame(form); tge_frame.grid(row=row_num, column=1, columnspan=2, sticky="w")
        tge_q_combo = ttk.Combobox(tge_frame, values=['Q1', 'Q2', 'Q3', 'Q4'], state="readonly", width=10); tge_q_combo.pack(side="left", padx=(0, 10))
        tge_year_entry = ttk.Entry(tge_frame, width=35); tge_year_entry.pack(side="left")
        widgets['TGE_Q'] = tge_q_combo; widgets['TGE_Year'] = tge_year_entry; row_num += 1
        for field in ["LinkGarapan", "KodeReferal"]:
            ttk.Label(form, text=f"{field}:").grid(row=row_num, column=0, sticky="w", pady=5)
            entry = ttk.Entry(form, width=50); entry.grid(row=row_num, column=1, columnspan=2, pady=5)
            widgets[field] = entry; row_num += 1
        ttk.Label(form, text="Status:").grid(row=row_num, column=0, sticky="w", pady=5)
        status_combo = ttk.Combobox(form, values=['Ongoing', 'Distributed', 'End'], state="readonly", width=47)
        status_combo.grid(row=row_num, column=1, columnspan=2, pady=5); widgets['Status'] = status_combo; row_num += 1
        ttk.Label(form, text="Info Listing:").grid(row=row_num, column=0, sticky="w", pady=5)
        listing_frame = ttk.Frame(form); listing_frame.grid(row=row_num, column=1, columnspan=2, sticky="w")
        listing_q_combo = ttk.Combobox(listing_frame, values=['Q1', 'Q2', 'Q3', 'Q4'], state="readonly", width=10); listing_q_combo.pack(side="left", padx=(0, 10))
        listing_year_entry = ttk.Entry(listing_frame, width=35); listing_year_entry.pack(side="left")
        widgets['Listing_Q'] = listing_q_combo; widgets['Listing_Year'] = listing_year_entry; row_num += 1
        
        # --- Mengisi widget dengan data yang ada ---
        # `full_data` adalah tuple: (ID, NamaProject, KapanMulai, Jaringan, Fase, Misi, ...)
        # Indeks kolom di tuple harus sesuai dengan urutan di `CREATE TABLE`
        widgets['NamaProject'].insert(0, full_data.NamaProject or "")
        widgets['KapanMulai'].insert(0, full_data.KapanMulai or "")
        widgets['Jaringan'].insert(0, full_data.Jaringan or "")
        widgets['Fase'].set(full_data.Fase or 'Testnet')
        
        # Logika untuk Misi
        misi_val = full_data.Misi or ""
        if misi_val in misi_options:
            widgets['Misi_combo'].set(misi_val)
        elif misi_val: # Jika ada isinya tapi tidak di daftar, berarti custom
            widgets['Misi_combo'].set('(isi sendiri)')
            widgets['Misi_custom'].config(state='normal')
            widgets['Misi_custom'].insert(0, misi_val)
        
        # Logika untuk memisahkan Quarter dan Tahun (TGE)
        tge_info_str = full_data.InfoTGE or ""
        tge_parts = tge_info_str.split()
        if len(tge_parts) > 0 and tge_parts[0] in ['Q1', 'Q2', 'Q3', 'Q4']:
            widgets['TGE_Q'].set(tge_parts[0])
            if len(tge_parts) > 1: widgets['TGE_Year'].insert(0, " ".join(tge_parts[1:]))
        else:
            widgets['TGE_Year'].insert(0, tge_info_str)
            
        widgets['LinkGarapan'].insert(0, full_data.LinkGarapan or "")
        widgets['KodeReferal'].insert(0, full_data.KodeReferal or "")
        widgets['Status'].set(full_data.Status or 'Ongoing')
        
        # Logika untuk memisahkan Quarter dan Tahun (Listing)
        listing_info_str = full_data.InfoListing or ""
        listing_parts = listing_info_str.split()
        if len(listing_parts) > 0 and listing_parts[0] in ['Q1', 'Q2', 'Q3', 'Q4']:
            widgets['Listing_Q'].set(listing_parts[0])
            if len(listing_parts) > 1: widgets['Listing_Year'].insert(0, " ".join(listing_parts[1:]))
        else:
            widgets['Listing_Year'].insert(0, listing_info_str)

        # Fungsi 'do_update' (logikanya mirip 'do_tambah')
        def do_update():
            data = {}
            for field in ["NamaProject", "KapanMulai", "Jaringan", "LinkGarapan", "KodeReferal"]: data[field] = widgets[field].get()
            data['Fase'] = widgets['Fase'].get()
            if widgets['Misi_combo'].get() == "(isi sendiri)": data['Misi'] = widgets['Misi_custom'].get()
            else: data['Misi'] = widgets['Misi_combo'].get()
            tge_q = widgets['TGE_Q'].get(); tge_y = widgets['TGE_Year'].get(); data['InfoTGE'] = f"{tge_q} {tge_y}".strip()
            data['Status'] = widgets['Status'].get()
            list_q = widgets['Listing_Q'].get(); list_y = widgets['Listing_Year'].get(); data['InfoListing'] = f"{list_q} {list_y}".strip()
            if not data["NamaProject"] or not data["KapanMulai"] or not data["Jaringan"] or not data["Status"]:
                messagebox.showwarning("Input Kosong", "Kolom NamaProject, KapanMulai, Jaringan, dan Status harus diisi.", parent=dialog); return
            
            conn_upd = self.get_connection(DB_PROJECT)
            if conn_upd:
                cursor_upd = conn_upd.cursor()
                sql = "UPDATE Project SET NamaProject=?, KapanMulai=?, Jaringan=?, Fase=?, Misi=?, InfoTGE=?, LinkGarapan=?, KodeReferal=?, Status=?, InfoListing=? WHERE ID=?"
                values = (data['NamaProject'], data['KapanMulai'], data['Jaringan'], data['Fase'], data['Misi'], data['InfoTGE'], data['LinkGarapan'], data['KodeReferal'], data['Status'], data['InfoListing'], project_id)
                cursor_upd.execute(sql, values); conn_upd.commit(); cursor_upd.close(); conn_upd.close()
                messagebox.showinfo("Sukses", "Data proyek berhasil diupdate.", parent=dialog); dialog.destroy(); self.muat_ulang_data()
        
        ttk.Button(dialog, text="Simpan Perubahan", command=do_update).pack(pady=20)
        
    def buka_dialog_hapus(self):
        selected_item = self.tree.focus()
        if not selected_item: messagebox.showinfo("Informasi", "Pilih salah satu proyek dari tabel untuk dihapus."); return
        item_values = self.tree.item(selected_item, 'values'); project_id = item_values[0]; project_name = item_values[1]
        if messagebox.askyesno("Konfirmasi Akhir", f"ANDA YAKIN ingin menghapus permanen data proyek:\n\n{project_name}?", icon='warning'):
            conn_del = self.get_connection(DB_PROJECT)
            if conn_del:
                cursor_del = conn_del.cursor(); cursor_del.execute("DELETE FROM Project WHERE ID=?", project_id); conn_del.commit(); cursor_del.close(); conn_del.close()
                messagebox.showinfo("Sukses", "Data berhasil dihapus."); self.muat_ulang_data()
                
# --- ALUR UTAMA PROGRAM ---
if __name__ == "__main__":
    while True:
        # Jalankan Jendela Login
        login_root = tk.Tk()
        login_app = LoginWindow(login_root)
        login_root.mainloop()

        # Jika login berhasil, jalankan aplikasi utama
        if login_app.login_successful:
            main_root = tk.Tk()
            main_app = AplikasiProject(main_root)
            main_root.mainloop()
            
            # Jika user logout, loop kembali ke jendela login
            if main_app.user_logged_out:
                continue
            else: # Jika user menutup jendela utama (bukan logout), program berhenti
                break
        else: # Jika login gagal atau dibatalkan, program berhenti
            break
