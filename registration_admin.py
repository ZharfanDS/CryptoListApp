import bcrypt

password = input("Masukkan password baru untuk admin: ").encode('utf-8')

# Generate hash dari password
hashed = bcrypt.hashpw(password, bcrypt.gensalt())

# Tampilkan hash. Salin (copy) seluruh hasil ini.
print("\nPassword hash Anda adalah:")
print(hashed.decode('utf-8'))

print("\n-------------------------------------------------------------")
print("SEKARANG: Jalankan perintah dibawah, pakai SQL INSERT di SSMS untuk menyimpan user.")
print("Contoh: INSERT INTO Users (Username, PasswordHash) VALUES ('admin', 'HASIL_DARI_ATAS');")
print("-------------------------------------------------------------")
