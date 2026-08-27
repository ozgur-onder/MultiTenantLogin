import os
import secrets
import re
import hashlib
from datetime import datetime, timedelta
import psycopg2
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from cryptography.fernet import Fernet

# IP tabanlı hatalı deneme takibi (Brute Force koruması için)
ip_hata_takip = {}

def get_cipher():
    return Fernet(os.getenv("ENCRYPTION_KEY").encode('utf-8'))

def veritabani_baglantisi():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"), database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"), password=os.getenv("DB_PASS"), port=os.getenv("DB_PORT", "5432")
    )

async def sifre_sifirlama_islemini_yap(request, sicil, email):
    ip_adresi = request.client.host if request.client else "Bilinmiyor"
    su_an = datetime.now()
    
    # 1 saatlik blokaj kontrolleri
    cerez_hata = int(request.cookies.get("hatali_deneme_sayisi", 0))
    if ip_adresi in ip_hata_takip:
        if ip_hata_takip[ip_adresi]["sayi"] >= 5 and su_an < ip_hata_takip[ip_adresi]["blok_bitis"]:
            return {"icerik": {"detail": "Çok fazla hatalı deneme yaptınız. 1 saat sonra tekrar deneyin."}, "statu": 429}
    
    if cerez_hata >= 5:
        return {"icerik": {"detail": "Çok fazla hatalı deneme yaptınız. 1 saat sonra tekrar deneyin."}, "statu": 429}

    conn = cursor = None
    try:
        conn = veritabani_baglantisi()
        cursor = conn.cursor()

        cursor.execute("SELECT sicil FROM kullanicilar WHERE sicil = %s AND email = %s AND durum = TRUE;", (sicil, email))
        user = cursor.fetchone()

        if not user:
            # Hatalı deneme artırımı
            if ip_adresi not in ip_hata_takip or su_an > ip_hata_takip[ip_adresi]["blok_bitis"]:
                ip_hata_takip[ip_adresi] = {"sayi": 1, "blok_bitis": su_an + timedelta(hours=1)}
            else:
                ip_hata_takip[ip_adresi]["sayi"] += 1

            return {
                "icerik": {"detail": "Bu bilgilerle kullanıcı bulunamamıştır."},
                "statu": 400,
                "cerez_ekle": {"key": "hatali_deneme_sayisi", "value": str(cerez_hata + 1), "max_age": 3600, "httponly": True}
            }

        # Başarılı giriş, blokeleri sıfırla
        if ip_adresi in ip_hata_takip:
            del ip_hata_takip[ip_adresi]

        cursor.execute("SELECT sunucu, port, kullanici_adi, sifre, gonderici_adi FROM smtp_ayarlari WHERE id = 1;")
        sunucu, port, kullanici_adi, kilitli_smtp_sifre, gonderici_adi = cursor.fetchone()
        smtp_sifre = get_cipher().decrypt(kilitli_smtp_sifre.encode('utf-8')).decode('utf-8')

        token = secrets.token_urlsafe(32)
        cursor.execute("""
            INSERT INTO sifre_sifirlama_talepleri (sicil, token, gecerlilik_suresi, kullanildi, ip_adresi)
            VALUES (%s, %s, %s, FALSE, %s)
        """, (sicil, token, su_an + timedelta(hours=1), ip_adresi))

        # E-posta içeriği
        base_url = os.getenv("BASE_URL", "http://localhost:5000").rstrip("/")
        link = f"{base_url}/sayfalar/sifre_yenile?token={token}"
        msg = MIMEMultipart()
        msg['From'] = f"{gonderici_adi} <{kullanici_adi}>"
        msg['To'] = email
        msg['Subject'] = "Şifre Sıfırlama Talebi"
        msg.attach(MIMEText(f"Şifre sıfırlama linkiniz (1 saat geçerlidir):\n\n{link}", 'plain', 'utf-8'))

        server = smtplib.SMTP_SSL(sunucu, int(port), timeout=15) if int(port) == 465 else smtplib.SMTP(sunucu, int(port), timeout=15)
        if int(port) != 465: server.starttls()
        server.login(kullanici_adi, smtp_sifre)
        server.sendmail(kullanici_adi, email, msg.as_string())
        server.quit()
        
        conn.commit()
        return {"icerik": {"mesaj": "Şifre sıfırlama bağlantısı gönderildi."}, "statu": 200, "cerez_sil": "hatali_deneme_sayisi"}

    except Exception as e:
        if conn: conn.rollback()
        return {"icerik": {"detail": "Sistemde bir hata oluştu."}, "statu": 400}
    finally:
        if cursor: cursor.close()
        if conn: conn.close()


async def yeni_sifreyi_kaydet(token, yeni_sifre):
    # Şifre Karmaşıklık Kontrolü (Min 12, Büyük, Küçük, Özel Karakter)
    karmasiklik_kurali = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#$%^&*(),.?\":{}|<>]).{12,}$"
    if not re.match(karmasiklik_kurali, yeni_sifre):
        return {"icerik": {"detail": "Şifreniz en az 12 karakter olmalı, büyük/küçük harf ve özel karakter (ör: !) içermelidir."}, "statu": 400}

    conn = cursor = None
    try:
        conn = veritabani_baglantisi()
        cursor = conn.cursor()

        # Gönderilen bağlantının doğruluğu ve süresi kontrol edilir
        cursor.execute("""
            SELECT sicil FROM sifre_sifirlama_talepleri 
            WHERE token = %s AND kullanildi = FALSE AND gecerlilik_suresi > %s
        """, (token, datetime.now()))
        
        talep = cursor.fetchone()
        
        if not talep:
            return {"icerik": {"detail": "Bağlantınız geçersiz veya süresi (1 saat) dolmuş."}, "statu": 400}
            
        sicil = talep[0]
        
        # Şifre maskelenir
        sifre_hash = hashlib.sha256(yeni_sifre.encode('utf-8')).hexdigest()

        # Veritabanında şifreyi güncelle ve bağlantıyı "kullanıldı" yap
        cursor.execute("UPDATE kullanicilar SET parola = %s WHERE sicil = %s", (sifre_hash, sicil))
        cursor.execute("UPDATE sifre_sifirlama_talepleri SET kullanildi = TRUE WHERE token = %s", (token,))
        
        conn.commit()
        
        return {"icerik": {"mesaj": "Şifreniz başarıyla güncellendi."}, "statu": 200}

    except Exception:
        if conn: conn.rollback()
        return {"icerik": {"detail": "Bir hata oluştu, lütfen tekrar deneyin."}, "statu": 400}
    finally:
        if cursor: cursor.close()
        if conn: conn.close()