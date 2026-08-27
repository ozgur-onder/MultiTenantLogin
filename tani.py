import os
import psycopg2
import smtplib
from cryptography.fernet import Fernet

# ─── 1. ENCRYPTION_KEY ──────────────────────────────────────────────────────
print("=== 1. ENCRYPTION_KEY ===")
key = os.getenv("ENCRYPTION_KEY")
if not key:
    print("HATA: ENCRYPTION_KEY .env'de tanımlı değil!")
    exit(1)
print(f"OK — uzunluk: {len(key)} karakter")

# ─── 2. DB Bağlantısı ───────────────────────────────────────────────────────
print("\n=== 2. DB Bağlantısı ===")
try:
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"), database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"), password=os.getenv("DB_PASS"),
        port=os.getenv("DB_PORT", "5432")
    )
    c = conn.cursor()
    print("OK")
except Exception as e:
    print(f"HATA: {e}")
    exit(1)

# ─── 3. smtp_ayarlari Satırı ─────────────────────────────────────────────────
print("\n=== 3. smtp_ayarlari (id=1) ===")
c.execute("SELECT id, sunucu, port, sifre, kullanici_adi FROM smtp_ayarlari WHERE id = 1;")
row = c.fetchone()
if not row:
    print("HATA: id=1 satırı yok!")
    c.execute("SELECT id, sunucu FROM smtp_ayarlari;")
    rows = c.fetchall()
    print("Mevcut satırlar:", rows if rows else "Tablo tamamen boş!")
    conn.close()
    exit(1)
smtp_id, smtp_sunucu, smtp_port, smtp_sifre_hash, smtp_kullanici = row
print(f"OK — sunucu: {smtp_sunucu}, port: {smtp_port}")
print(f"     Kayıtlı sifre (ilk 20 karakter): {smtp_sifre_hash[:20]}...")

# ─── 4. Fernet Decrypt ──────────────────────────────────────────────────────
print("\n=== 4. Fernet Decrypt ===")
try:
    cipher = Fernet(key.encode("utf-8"))
    decrypted = cipher.decrypt(smtp_sifre_hash.encode("utf-8")).decode("utf-8")
    print(f"OK — şifre çözüldü ({len(decrypted)} karakter)")
except Exception as e:
    print(f"HATA: {type(e).__name__}: {e}")
    print("\nMuhtemel neden: SMTP şifresi farklı bir ENCRYPTION_KEY ile şifrelenmiş.")
    print("Çözüm: SMTP şifresini mevcut key ile yeniden şifrele:")
    print(f"  docker exec bi_app python3 -c \"from cryptography.fernet import Fernet; import os; c=Fernet(os.getenv('ENCRYPTION_KEY').encode()); print(c.encrypt(b'SMTP_SIFREN').decode())\"")
    conn.close()
    exit(1)

# ─── 5. SMTP Bağlantı ───────────────────────────────────────────────────────
print("\n=== 5. SMTP Bağlantı Testi ===")
try:
    if int(smtp_port) == 465:
        server = smtplib.SMTP_SSL(smtp_sunucu, int(smtp_port), timeout=10)
    else:
        server = smtplib.SMTP(smtp_sunucu, int(smtp_port), timeout=10)
        server.starttls()
    server.login(smtp_kullanici, decrypted)
    print("OK — giriş başarılı!")
    server.quit()
except Exception as e:
    print(f"HATA: {type(e).__name__}: {e}")

conn.close()
print("\n=== Tanı tamamlandı ===")