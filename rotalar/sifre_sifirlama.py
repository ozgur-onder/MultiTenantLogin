import os
import secrets
from datetime import datetime, timedelta
from fastapi import APIRouter, Form, HTTPException
from fastapi.responses import JSONResponse
import psycopg2
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

router = APIRouter()

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
        conn = veritabani_baglantisi()
        cursor = conn.cursor()

        cursor.execute("SELECT sicil FROM kullanicilar WHERE sicil = %s AND email = %s AND durum = TRUE;", (sicil, email))
        user = cursor.fetchone()
        if not user:
            cursor.close()
            raise HTTPException(status_code=404, detail="Girilen bilgilerle eşleşen aktif bir kullanıcı bulunamadı.")

        cursor.execute("SELECT sunucu, port, kullanici_adi, sifre, gonderici_adi FROM smtp_ayarlari WHERE id = 1;")
        smtp_ayar = cursor.fetchone()
        if not smtp_ayar:
            cursor.close()
            raise HTTPException(status_code=500, detail="Sistemde tanımlı ID 1 numaralı SMTP ayarı bulunamadı.")

        sunucu, port, kullanici_adi, smtp_sifre, gonderici_adi = smtp_ayar

        token = secrets.token_urlsafe(32)
        gecerlilik_suresi = datetime.now() + timedelta(minutes=15)

        cursor.execute("""
            INSERT INTO sifre_sifirlama_talepleri (sicil, token, gecerlilik_suresi, kullanildi)
            VALUES (%s, %s, %s, FALSE)
        """, (sicil, token, gecerlilik_suresi))
        
        conn.commit()
        cursor.close()

        sifirlama_linki = f"http://localhost:5000/sayfalar/sifre_yenile?token={token}"
        
        msg = MIMEMultipart()
        msg['From'] = f"{gonderici_adi} <{kullanici_adi}>"
        msg['To'] = email
        msg['Subject'] = "İş Zekası Platformu - Şifre Sıfırlama Talebi"

        body = f"""Merhaba,\n\nHesabınız için bir şifre sıfırlama talebinde bulunuldu.\nŞifrenizi yenilemek için aşağıdaki bağlantıya tıklayabilirsiniz:\n\n{sifirlama_linki}\n\nBu bağlantı 15 dakika süreyle geçerlidir.\nEğer bu talebi siz yapmadıysanız, bu e-postayı dikkate almayınız.\n\nİyi çalışmalar,\n{gonderici_adi}"""
        msg.attach(MIMEText(body, 'plain', 'utf-8'))

        if int(port) == 465:
            server = smtplib.SMTP_SSL(sunucu, int(port))
        else:
            server = smtplib.SMTP(sunucu, int(port))
            server.starttls()
        server.login(kullanici_adi, smtp_sifre)
        server.sendmail(kullanici_adi, email, msg.as_string())
        server.quit()

        return JSONResponse(
            content={"mesaj": "Şifre sıfırlama bağlantısı e-posta adresinize gönderildi."}, 
            status_code=200
        )

    except HTTPException as he:
        raise he
    except Exception as e:
        if conn:
            conn.rollback()
        raise HTTPException(status_code=500, detail=f"İşlem sırasında hata oluştu: {str(e)}")
    finally:
        if conn:
            conn.close()