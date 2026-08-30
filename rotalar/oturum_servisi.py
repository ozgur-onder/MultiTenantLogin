import secrets
import sys
from datetime import datetime, timedelta
import os
import psycopg2

# Oturum süresi (dakika)
OTURUM_SURESI_DK = int(os.getenv("OTURUM_SURESI_DK", "480"))  # varsayılan 8 saat

def db_baglan():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"), database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"), password=os.getenv("DB_PASS"),
        port=os.getenv("DB_PORT", "5432")
    )

async def oturum_olustur(cursor, sicil: str, ip: str, tarayici: str) -> str:
    """Yeni oturum oluşturur, token döndürür. Mevcut cursor üzerinde çalışır."""
    token = secrets.token_urlsafe(48)
    cursor.execute(
        """INSERT INTO kullanici_oturumlari
           (sicil, oturum_token, ip_adresi, tarayici, durum)
           VALUES (%s, %s, %s, %s, 'aktif')""",
        (sicil, token, ip, tarayici)
    )
    return token

async def oturum_dogrula(token: str) -> dict | None:
    """
    Token geçerliyse kullanıcı bilgilerini döndürür.
    Geçersiz veya süresi dolmuşsa None döndürür.
    Geçerliyse son_aktivite_zamani güncellenir.
    """
    if not token:
        return None

    conn = cursor = None
    try:
        conn   = db_baglan()
        cursor = conn.cursor()

        sinir = datetime.now() - timedelta(minutes=OTURUM_SURESI_DK)

        cursor.execute(
            """SELECT o.sicil, k.ad, k.soyad, k.email
               FROM kullanici_oturumlari o
               JOIN kullanicilar k ON k.sicil = o.sicil
               WHERE o.oturum_token = %s
                 AND o.durum = 'aktif'
                 AND o.son_aktivite_zamani > %s""",
            (token, sinir)
        )
        satir = cursor.fetchone()

        if not satir:
            return None

        sicil, ad, soyad, email = satir

        # Aktivite zamanını güncelle
        cursor.execute(
            """UPDATE kullanici_oturumlari
               SET son_aktivite_zamani = NOW()
               WHERE oturum_token = %s""",
            (token,)
        )
        conn.commit()

        return {"sicil": sicil, "ad": ad, "soyad": soyad,
                "ad_soyad": f"{ad} {soyad}", "email": email}

    except Exception as e:
        print(f"[oturum_servisi] dogrula {type(e).__name__}: {e}", file=sys.stderr)
        return None
    finally:
        if cursor: cursor.close()
        if conn:   conn.close()

async def oturum_sonlandir(token: str) -> bool:
    """Oturumu kapatır, cikis_zamani ve durum güncellenir."""
    if not token:
        return False

    conn = cursor = None
    try:
        conn   = db_baglan()
        cursor = conn.cursor()
        cursor.execute(
            """UPDATE kullanici_oturumlari
               SET durum = 'kapali', cikis_zamani = NOW()
               WHERE oturum_token = %s AND durum = 'aktif'""",
            (token,)
        )
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"[oturum_servisi] sonlandir {type(e).__name__}: {e}", file=sys.stderr)
        if conn: conn.rollback()
        return False
    finally:
        if cursor: cursor.close()
        if conn:   conn.close()