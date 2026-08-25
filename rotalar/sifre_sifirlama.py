import os
import secrets
from datetime import datetime, timedelta
from fastapi import APIRouter, Form
from fastapi.responses import JSONResponse
import psycopg2
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from cryptography.fernet import Fernet

router = APIRouter()

def get_cipher():
    key = os.getenv("ENCRYPTION_KEY")
    if not key:
        raise Exception("Sistem Hatası: ENCRYPTION_KEY .env dosyasında bulunamadı!")
    return Fernet(key.encode('utf-8'))

def veritabani_baglantisi():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        port=os.getenv("DB_PORT", "5432")
    )

@router.post("/sifre-sifirla-talep")
async def sifre_sifirla_talep(
    sicil: str = Form(...),
    email: str = Form(...)
):
    conn = None
    try:
        # Şifreleme aracını burada çağırıyoruz
        cipher_suite = get_cipher()

        conn = veritabani_baglantisi()
        cursor = conn.cursor()

        cursor.execute("SELECT sicil FROM kullanicilar WHERE sicil = %s AND email = %s AND durum = TRUE;", (sicil, email))
        user = cursor.fetchone()
        if not user:
            raise Exception("Girilen bilgilerle eşleşen aktif bir kullanıcı bulunamadı.")

        cursor.execute("SELECT sunucu, port, kullanici_adi, sifre, gonderici_adi FROM smtp_ayarlari WHERE id = 1;")
        smtp_ayar = cursor.fetchone()
        if not smtp_ayar:
            raise Exception("Sistemde tanımlı SMTP ayarı bulunamadı. Lütfen yöneticiye başvurun.")

        sunucu, port, kullanici_adi, kilitli_smtp_sifre, gonderici_adi = smtp_ayar
        
        # Veritabanından gelen kilitli şifreyi çözüyoruz
        smtp_sifre = cipher_suite.decrypt(kilitli_smtp_sifre.encode('utf-8')).decode('utf-8')

        token = secrets.token_urlsafe(32)
        gecerlilik_suresi = datetime.now() + timedelta(minutes=15)

        cursor.execute("""
            INSERT INTO sifre_sifirlama_talepleri (sicil, token, gecerlilik_suresi, kullanildi)
            VALUES (%s, %s, %s, FALSE)
        """, (sicil, token, gecerlilik_suresi))

        sifirlama_linki = f"http://localhost:5000/sayfalar/sifre_yenile?token={token}"
        
        msg = MIMEMultipart()
        msg['From'] = f"{gonderici_adi} <{kullanici_adi}>"
        msg['To'] = email
        msg['Subject'] = "İş Zekası Platformu - Şifre Sıfırlama Talebi"

        body = f"Merhaba,\n\nHesabınız için bir şifre sıfırlama talebinde bulunuldu.\nŞifrenizi yenilemek için aşağıdaki bağlantıya tıklayabilirsiniz:\n\n{sifirlama_linki}\n\nBu bağlantı 15 dakika süreyle geçerlidir.\nEğer bu talebi siz yapmadıysanız, bu e-postayı dikkate almayınız.\n\nİyi çalışmalar,\n{gonderici_adi}"
        msg.attach(MIMEText(body, 'plain', 'utf-8'))

        try:
            if int(port) == 465:
                server = smtplib.SMTP_SSL(sunucu, int(port), timeout=15)
            else:
                server = smtplib.SMTP(sunucu, int(port), timeout=15)
                server.starttls()
            server.login(kullanici_adi, smtp_sifre)
            server.sendmail(kullanici_adi, email, msg.as_string())
            server.quit()
        except Exception as mail_err:
            raise Exception(f"Mail sunucusuna bağlanılamadı. Hata Detayı: {str(mail_err)}")

        conn.commit()
        cursor.close()

        return JSONResponse(
            content={"mesaj": "Şifre sıfırlama bağlantısı e-posta adresinize gönderildi."}, 
            status_code=200
        )

    except Exception as e:
        if conn:
            conn.rollback() 
        return JSONResponse(content={"detail": str(e)}, status_code=400)
    finally:
        if conn:
            conn.close()