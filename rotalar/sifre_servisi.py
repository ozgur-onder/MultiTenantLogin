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

#IP tabanlı brute-force koruması (bellek içi)
ip_hata_takip = {}

def get_cipher():
    return Fernet(os.getenv("ENCRYPTION_KEY").encode("utf-8"))

def veritabani_baglantisi():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        port=os.getenv("DB_PORT", "5432")
    )

def _html_email_olustur(link: str, gonderici_adi: str) -> str:
    """Şifre sıfırlama için HTML e-posta şablonu."""
    return f"""<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<style>
  body {{margin:0;padding:0;background:#f1f5f9;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Arial,sans-serif;}}
  .wrap {{max-width:560px;margin:40px auto;background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,.08);}}
  .head {{background:linear-gradient(135deg,#1e40af 0%,#2563eb 100%);padding:36px 40px;text-align:center;}}
  .head svg {{margin-bottom:12px;}}
  .head h1 {{color:#fff;margin:0;font-size:22px;font-weight:700;letter-spacing:-.3px;}}
  .head p  {{color:rgba(255,255,255,.75);margin:6px 0 0;font-size:13px;}}
  .body {{padding:40px;}}
  .body h2 {{color:#111827;font-size:20px;margin:0 0 12px;font-weight:600;}}
  .body p  {{color:#4b5563;font-size:15px;line-height:1.65;margin:0 0 24px;}}
  .btn-wrap {{text-align:center;margin:32px 0;}}
  .btn {{display:inline-block;background:#2563eb;color:#fff!important;text-decoration:none;padding:14px 40px;border-radius:8px;font-size:15px;font-weight:600;letter-spacing:.2px;}}
  .fallback {{background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;padding:14px 16px;margin:0 0 24px;}}
  .fallback p  {{color:#6b7280;font-size:12px;margin:0 0 4px;}}
  .fallback a  {{color:#2563eb;font-size:12px;word-break:break-all;text-decoration:none;}}
  .warning {{background:#fef3c7;border-left:4px solid #f59e0b;border-radius:0 6px 6px 0;padding:12px 16px;margin:0 0 24px;}}
  .warning p   {{color:#92400e;font-size:13px;margin:0;line-height:1.5;}}
  .foot {{background:#f8fafc;border-top:1px solid #e5e7eb;padding:24px 40px;text-align:center;}}
  .foot p {{color:#9ca3af;font-size:12px;margin:0;line-height:1.7;}}
</style>
</head>
<body>
<div class="wrap">

  <div class="head">
    <svg width="40" height="40" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M3 3h2v18H3V3zm6 8h2v10H9V11zm6-5h2v15h-2V6zm6 4h2v11h-2v-11z" fill="rgba(255,255,255,0.9)"/>
    </svg>
    <h1>İş Zekası Platformu</h1>
    <p>Yerli ve milli iş zekası çözümü</p>
  </div>

  <div class="body">
    <h2>Şifre Sıfırlama Talebi</h2>
    <p>
      Hesabınız için bir şifre sıfırlama talebi aldık.<br>
      Yeni şifrenizi belirlemek için aşağıdaki butona tıklayın.
    </p>

    <div class="btn-wrap">
      <a href="{link}" class="btn">🔐&nbsp;&nbsp;Yeni Şifremi Belirle</a>
    </div>

    <div class="fallback">
      <p>Buton çalışmıyorsa bu adresi tarayıcınıza kopyalayın:</p>
      <a href="{link}">{link}</a>
    </div>

    <div class="warning">
      <p>
        ⏰ Bu bağlantı <strong>1 saat</strong> süreyle geçerlidir.<br>
        Bu talebi siz yapmadıysanız bu e-postayı dikkate almayınız —
        hesabınız güvende.
      </p>
    </div>
  </div>

  <div class="foot">
    <p>
      Bu e-posta <strong>{gonderici_adi}</strong> tarafından otomatik olarak gönderilmiştir.<br>
      Lütfen bu e-postayı yanıtlamayın.
    </p>
  </div>

</div>
</body>
</html>"""


async def sifre_sifirlama_islemini_yap(request, sicil, email):
    ip_adresi = request.client.host if request.client else "Bilinmiyor"
    su_an = datetime.now()

    # Brute-force: IP blok kontrolü
    cerez_hata = int(request.cookies.get("hatali_deneme_sayisi", 0))
    if ip_adresi in ip_hata_takip:
        kayit = ip_hata_takip[ip_adresi]
        if kayit["sayi"] >= 5 and su_an < kayit["blok_bitis"]:
            return {
                "icerik": {"detail": "Çok fazla hatalı deneme yaptınız. 1 saat sonra tekrar deneyin."},
                "statu": 429
            }
    if cerez_hata >= 5:
        return {
            "icerik": {"detail": "Çok fazla hatalı deneme yaptınız. 1 saat sonra tekrar deneyin."},
            "statu": 429
        }

    conn = cursor = None
    try:
        conn   = veritabani_baglantisi()
        cursor = conn.cursor()

        # Kullanıcı doğrulama
        cursor.execute(
            "SELECT sicil FROM kullanicilar WHERE sicil = %s AND email = %s AND durum = TRUE;",
            (sicil, email)
        )
        user = cursor.fetchone()

        if not user:
            # Hatalı deneme sayacını artır
            if ip_adresi not in ip_hata_takip or su_an > ip_hata_takip[ip_adresi]["blok_bitis"]:
                ip_hata_takip[ip_adresi] = {"sayi": 1, "blok_bitis": su_an + timedelta(hours=1)}
            else:
                ip_hata_takip[ip_adresi]["sayi"] += 1
            return {
                "icerik": {"detail": "Bu bilgilerle eşleşen aktif bir kullanıcı bulunamadı."},
                "statu": 400,
                "cerez_ekle": {
                    "key": "hatali_deneme_sayisi",
                    "value": str(cerez_hata + 1),
                    "max_age": 3600,
                    "httponly": True
                }
            }

        # Başarılı-- brute-force sayacını sıfırla
        ip_hata_takip.pop(ip_adresi, None)

        # SMTP ayarları
        cursor.execute(
            "SELECT sunucu, port, kullanici_adi, sifre, gonderici_adi FROM smtp_ayarlari WHERE id = 1;"
        )
        smtp_satir = cursor.fetchone()
        if not smtp_satir:
            raise Exception("Sistemde SMTP ayarı bulunamadı (id=1).")
        smtp_sunucu, smtp_port, kullanici_adi, kilitli_sifre, gonderici_adi = smtp_satir
        smtp_sifre = get_cipher().decrypt(kilitli_sifre.encode("utf-8")).decode("utf-8")

        #Token oluştur ve DB'ye yaz
        token            = secrets.token_urlsafe(32)
        gecerlilik_suresi = su_an + timedelta(hours=1)

        cursor.execute(
            """INSERT INTO sifre_sifirlama_talepleri
               (sicil, token, gecerlilik_suresi, kullanildi, ip_adresi)
               VALUES (%s, %s, %s, FALSE, %s)""",
            (sicil, token, gecerlilik_suresi, ip_adresi)
        )

        # E-posta gönder
        base_url = os.getenv("BASE_URL", "http://localhost:5000").rstrip("/")
        link     = f"{base_url}/sayfalar/sifre_yenile?token={token}"

        html_icerik = _html_email_olustur(link, gonderici_adi)
        duz_metin   = (
            f"Şifre sıfırlama linkiniz (1 saat geçerlidir):\n\n{link}\n\n"
            f"Bu talebi siz yapmadıysanız bu e-postayı dikkate almayınız."
        )

        msg              = MIMEMultipart("mixed")
        msg["From"]      = f"{gonderici_adi} <{kullanici_adi}>"
        msg["To"]        = email
        msg["Subject"]   = "İş Zekası Platformu – Şifre Sıfırlama Talebi"

        alternatif = MIMEMultipart("alternative")
        alternatif.attach(MIMEText(duz_metin,   "plain", "utf-8"))
        alternatif.attach(MIMEText(html_icerik, "html",  "utf-8"))
        msg.attach(alternatif)

        if int(smtp_port) == 465:
            server = smtplib.SMTP_SSL(smtp_sunucu, int(smtp_port), timeout=15)
        else:
            server = smtplib.SMTP(smtp_sunucu, int(smtp_port), timeout=15)
            server.starttls()

        server.login(kullanici_adi, smtp_sifre)
        server.sendmail(kullanici_adi, email, msg.as_string())
        server.quit()

        conn.commit()
        return {
            "icerik": {"mesaj": "Şifre sıfırlama bağlantısı e-posta adresinize gönderildi."},
            "statu": 200,
            "cerez_sil": "hatali_deneme_sayisi"
        }

    except Exception as e:
        # Hatayı Docker loglarına yaz
        print(f"[sifre_servisi] HATA: {type(e).__name__}: {e}", file=sys.stderr)
        if conn:
            conn.rollback()
        return {
            "icerik": {"detail": "Sistemde bir hata oluştu. Lütfen daha sonra tekrar deneyin."},
            "statu": 400
        }
    finally:
        if cursor: cursor.close()
        if conn:   conn.close()


async def yeni_sifreyi_kaydet(token, yeni_sifre):
    # Şifre karmaşıklık kuralı
    kural = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#$%^&*(),.?\":{}|<>]).{12,}$"
    if not re.match(kural, yeni_sifre):
        return {
            "icerik": {
                "detail": (
                    "Şifreniz en az 12 karakter olmalı; "
                    "büyük harf, küçük harf ve özel karakter (ör: !) içermelidir."
                )
            },
            "statu": 400
        }

    conn = cursor = None
    try:
        conn   = veritabani_baglantisi()
        cursor = conn.cursor()

        #Token doğrulama 
        cursor.execute(
            """SELECT sicil FROM sifre_sifirlama_talepleri
               WHERE token = %s AND kullanildi = FALSE AND gecerlilik_suresi > %s""",
            (token, datetime.now())
        )
        talep = cursor.fetchone()
        if not talep:
            return {
                "icerik": {"detail": "Bağlantınız geçersiz veya süresi (1 saat) dolmuş."},
                "statu": 400
            }

        sicil = talep[0]

        #Şifreyi hashle ve güncelle
        sifre_hash = hashlib.sha256(yeni_sifre.encode("utf-8")).hexdigest()
        cursor.execute(
            "UPDATE kullanicilar SET parola = %s WHERE sicil = %s",
            (sifre_hash, sicil)
        )
        cursor.execute(
            "UPDATE sifre_sifirlama_talepleri SET kullanildi = TRUE WHERE token = %s",
            (token,)
        )

        conn.commit()
        return {
            "icerik": {"mesaj": "Şifreniz başarıyla güncellendi. Giriş yapabilirsiniz."},
            "statu": 200
        }

    except Exception as e:
        print(f"[sifre_servisi] yeni_sifreyi_kaydet HATA: {type(e).__name__}: {e}", file=sys.stderr)
        if conn:
            conn.rollback()
        return {
            "icerik": {"detail": "Bir hata oluştu, lütfen tekrar deneyin."},
            "statu": 400
        }
    finally:
        if cursor: cursor.close()
        if conn:   conn.close()