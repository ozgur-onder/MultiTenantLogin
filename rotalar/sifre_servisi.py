import os
import sys
import secrets
import re
import hashlib
from datetime import datetime, timedelta

import psycopg2
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from cryptography.fernet import Fernet
from jinja2 import Environment, FileSystemLoader

# ── Sabitler ──────────────────────────────────────────────────────────────────
BASE_DIR       = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EMAIL_SABLON_D = os.path.join(BASE_DIR, "dosyalar", "email_sablonlari")

# IP tabanlı brute-force koruması (bellek içi)
ip_hata_takip: dict = {}

# ── Yardımcı fonksiyonlar ─────────────────────────────────────────────────────
def get_cipher() -> Fernet:
    return Fernet(os.getenv("ENCRYPTION_KEY").encode("utf-8"))

def db_baglan() -> psycopg2.extensions.connection:
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        port=os.getenv("DB_PORT", "5432")
    )

def email_sablon_yukle(sablon_adi: str, **degiskenler) -> str:
    """Jinja2 ile e-posta şablonunu dosyadan yükler, değişkenleri doldurur."""
    env    = Environment(loader=FileSystemLoader(EMAIL_SABLON_D), autoescape=True)
    sablon = env.get_template(sablon_adi)
    return sablon.render(**degiskenler)

# ── Şifre sıfırlama talebi ────────────────────────────────────────────────────
async def sifre_sifirlama_islemini_yap(request, sicil: str, email: str) -> dict:
    ip_adresi = request.client.host if request.client else "bilinmiyor"
    su_an     = datetime.now()

    cerez_hata = int(request.cookies.get("hatali_deneme_sayisi", 0))
    kayit      = ip_hata_takip.get(ip_adresi)
    if (kayit and kayit["sayi"] >= 5 and su_an < kayit["blok_bitis"]) or cerez_hata >= 5:
        return {"icerik": {"detail": "Çok fazla hatalı deneme. 1 saat sonra tekrar deneyin."}, "statu": 429}

    conn = cursor = None
    try:
        conn   = db_baglan()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT sicil FROM kullanicilar WHERE sicil=%s AND email=%s AND durum=TRUE;",
            (sicil, email)
        )
        if not cursor.fetchone():
            if not kayit or su_an > kayit["blok_bitis"]:
                ip_hata_takip[ip_adresi] = {"sayi": 1, "blok_bitis": su_an + timedelta(hours=1)}
            else:
                ip_hata_takip[ip_adresi]["sayi"] += 1
            return {
                "icerik":     {"detail": "Bu bilgilerle eşleşen aktif kullanıcı bulunamadı."},
                "statu":      400,
                "cerez_ekle": {"key": "hatali_deneme_sayisi", "value": str(cerez_hata + 1),
                               "max_age": 3600, "httponly": True}
            }

        ip_hata_takip.pop(ip_adresi, None)

        cursor.execute(
            "SELECT sunucu, port, kullanici_adi, sifre, gonderici_adi FROM smtp_ayarlari WHERE id=1;"
        )
        smtp = cursor.fetchone()
        if not smtp:
            raise Exception("SMTP ayarı bulunamadı (id=1).")
        smtp_sunucu, smtp_port, kull_adi, kilitli_sifre, gonderici_adi = smtp
        smtp_sifre = get_cipher().decrypt(kilitli_sifre.encode()).decode()

        token             = secrets.token_urlsafe(32)
        gecerlilik_suresi = su_an + timedelta(hours=1)
        cursor.execute(
            "INSERT INTO sifre_sifirlama_talepleri "
            "(sicil, token, gecerlilik_suresi, kullanildi, ip_adresi) "
            "VALUES (%s, %s, %s, FALSE, %s)",
            (sicil, token, gecerlilik_suresi, ip_adresi)
        )

        base_url    = os.getenv("BASE_URL", "http://localhost:5000").rstrip("/")
        link        = f"{base_url}/sayfalar/sifre_yenile?token={token}"
        html_icerik = email_sablon_yukle("sifre_sifirlama.html", link=link, gonderici_adi=gonderici_adi)
        duz_metin   = f"Şifre sıfırlama linkiniz (1 saat geçerlidir):\n\n{link}"

        msg            = MIMEMultipart("mixed")
        msg["From"]    = f"{gonderici_adi} <{kull_adi}>"
        msg["To"]      = email
        msg["Subject"] = "İş Zekası Platformu – Şifre Sıfırlama Talebi"
        alternatif     = MIMEMultipart("alternative")
        alternatif.attach(MIMEText(duz_metin,   "plain", "utf-8"))
        alternatif.attach(MIMEText(html_icerik, "html",  "utf-8"))
        msg.attach(alternatif)

        if int(smtp_port) == 465:
            server = smtplib.SMTP_SSL(smtp_sunucu, int(smtp_port), timeout=15)
        else:
            server = smtplib.SMTP(smtp_sunucu, int(smtp_port), timeout=15)
            server.starttls()
        server.login(kull_adi, smtp_sifre)
        server.sendmail(kull_adi, email, msg.as_string())
        server.quit()

        conn.commit()
        return {
            "icerik":    {"mesaj": "Şifre sıfırlama bağlantısı e-posta adresinize gönderildi."},
            "statu":     200,
            "cerez_sil": "hatali_deneme_sayisi"
        }

    except Exception as e:
        print(f"[sifre_servisi] {type(e).__name__}: {e}", file=sys.stderr)
        if conn: conn.rollback()
        return {"icerik": {"detail": "Sistemde bir hata oluştu. Lütfen daha sonra tekrar deneyin."}, "statu": 400}
    finally:
        if cursor: cursor.close()
        if conn:   conn.close()


# ── Yeni şifre kaydetme ───────────────────────────────────────────────────────
async def yeni_sifreyi_kaydet(token: str, yeni_sifre: str) -> dict:
    KURAL = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#$%^&*(),.?":{}|<>]).{12,}$'
    if not re.match(KURAL, yeni_sifre):
        return {
            "icerik": {"detail": "Şifre en az 12 karakter, büyük/küçük harf ve özel karakter içermelidir."},
            "statu":  400
        }

    conn = cursor = None
    try:
        conn   = db_baglan()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT sicil FROM sifre_sifirlama_talepleri "
            "WHERE token=%s AND kullanildi=FALSE AND gecerlilik_suresi>%s",
            (token, datetime.now())
        )
        talep = cursor.fetchone()
        if not talep:
            return {"icerik": {"detail": "Bağlantı geçersiz veya süresi (1 saat) dolmuş."}, "statu": 400}

        sifre_hash = hashlib.sha256(yeni_sifre.encode()).hexdigest()
        cursor.execute("UPDATE kullanicilar SET parola=%s WHERE sicil=%s", (sifre_hash, talep[0]))
        cursor.execute("UPDATE sifre_sifirlama_talepleri SET kullanildi=TRUE WHERE token=%s", (token,))
        conn.commit()
        return {"icerik": {"mesaj": "Şifreniz başarıyla güncellendi. Giriş yapabilirsiniz."}, "statu": 200}

    except Exception as e:
        print(f"[sifre_servisi] yeni_sifreyi_kaydet {type(e).__name__}: {e}", file=sys.stderr)
        if conn: conn.rollback()
        return {"icerik": {"detail": "Bir hata oluştu, lütfen tekrar deneyin."}, "statu": 400}
    finally:
        if cursor: cursor.close()
        if conn:   conn.close()