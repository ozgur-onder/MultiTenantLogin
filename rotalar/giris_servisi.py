import hashlib
import sys
from fastapi import Request
import psycopg2
import os
from rotalar.oturum_servisi import oturum_olustur

def db_baglan():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"), database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"), password=os.getenv("DB_PASS"),
        port=os.getenv("DB_PORT", "5432")
    )

def _sifre_hashle(sifre: str) -> str:
    return hashlib.sha256(sifre.encode("utf-8")).hexdigest()

def _tarayici_al(request: Request) -> str:
    return request.headers.get("user-agent", "bilinmiyor")[:255]

def _ip_al(request: Request) -> str:
    return request.client.host if request.client else "bilinmiyor"

def _giris_logu_yaz(cursor, sicil: str, durum: str,
                    ip: str, tarayici: str, hata: str = None):
    cursor.execute(
        """INSERT INTO kullanici_giris_loglari
           (sicil, durum, ip_adresi, tarayici, hata_mesaji)
           VALUES (%s, %s, %s, %s, %s)""",
        (sicil, durum, ip, tarayici, hata)
    )

async def giris_yap(request: Request, eposta: str, sifre: str) -> dict:
    ip       = _ip_al(request)
    tarayici = _tarayici_al(request)
    conn = cursor = None

    try:
        conn   = db_baglan()
        cursor = conn.cursor()

        # Kullanıcıyı e-posta ile bul
        cursor.execute(
            """SELECT sicil, ad, soyad, parola, durum
               FROM kullanicilar
               WHERE email = %s""",
            (eposta,)
        )
        kullanici = cursor.fetchone()

        # Kullanıcı bulunamadı
        if not kullanici:
            _giris_logu_yaz(cursor, "bilinmiyor", "basarisiz", ip, tarayici,
                            "E-posta adresi bulunamadı.")
            conn.commit()
            return {"icerik": {"detail": "E-posta veya şifre hatalı."}, "statu": 401}

        sicil, ad, soyad, kayitli_hash, durum = kullanici

        # Hesap pasif
        if not durum:
            _giris_logu_yaz(cursor, sicil, "basarisiz", ip, tarayici,
                            "Pasif hesap girişimi.")
            conn.commit()
            return {"icerik": {"detail": "Hesabınız pasif durumda. Yöneticinizle iletişime geçin."}, "statu": 403}

        # Şifre doğrulama
        if _sifre_hashle(sifre) != kayitli_hash:
            _giris_logu_yaz(cursor, sicil, "basarisiz", ip, tarayici,
                            "Hatalı şifre.")
            conn.commit()
            return {"icerik": {"detail": "E-posta veya şifre hatalı."}, "statu": 401}

        # Başarılı giriş — oturum oluştur
        token = await oturum_olustur(cursor, sicil, ip, tarayici)
        _giris_logu_yaz(cursor, sicil, "basarili", ip, tarayici)
        conn.commit()

        return {
            "icerik": {"mesaj": "Giriş başarılı.", "ad_soyad": f"{ad} {soyad}"},
            "statu":  200,
            "token":  token
        }

    except Exception as e:
        print(f"[giris_servisi] {type(e).__name__}: {e}", file=sys.stderr)
        if conn: conn.rollback()
        return {"icerik": {"detail": "Sistemde bir hata oluştu."}, "statu": 500}
    finally:
        if cursor: cursor.close()
        if conn:   conn.close()