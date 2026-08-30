import sys
import psycopg2, os
from datetime import datetime

def db_baglan():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"), database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"), password=os.getenv("DB_PASS"),
        port=os.getenv("DB_PORT", "5432")
    )

async def firma_listesi() -> dict:
    conn = cursor = None
    try:
        conn   = db_baglan()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT firma_kodu, firma_adi, durum, olusturma_guncelleme_zamani FROM firma ORDER BY firma_adi"
        )
        satırlar = cursor.fetchall()
        firmalar = [
            {"firma_kodu": r[0], "firma_adi": r[1],
             "durum": r[2], "zaman": r[3].isoformat()}
            for r in satırlar
        ]
        return {"icerik": firmalar, "statu": 200}
    except Exception as e:
        print(f"[firma_servisi] listele {type(e).__name__}: {e}", file=sys.stderr)
        return {"icerik": {"detail": "Firmalar alınamadı."}, "statu": 500}
    finally:
        if cursor: cursor.close()
        if conn:   conn.close()

async def firma_ekle(firma_kodu: str, firma_adi: str, islem_yapan_sicil: str) -> dict:
    conn = cursor = None
    try:
        conn   = db_baglan()
        cursor = conn.cursor()

        # Mükerrer kontrol
        cursor.execute("SELECT 1 FROM firma WHERE firma_kodu=%s", (firma_kodu,))
        if cursor.fetchone():
            return {"icerik": {"detail": "Bu firma kodu zaten kayıtlı."}, "statu": 409}

        cursor.execute(
            """INSERT INTO firma (firma_kodu, firma_adi, olusturan_guncelleyen_sicil)
               VALUES (%s, %s, %s)""",
            (firma_kodu, firma_adi, islem_yapan_sicil)
        )
        conn.commit()
        return {"icerik": {"mesaj": "Firma başarıyla eklendi."}, "statu": 201}
    except Exception as e:
        print(f"[firma_servisi] ekle {type(e).__name__}: {e}", file=sys.stderr)
        if conn: conn.rollback()
        return {"icerik": {"detail": "Firma eklenemedi."}, "statu": 500}
    finally:
        if cursor: cursor.close()
        if conn:   conn.close()

async def firma_durum_guncelle(firma_kodu: str, yeni_durum: bool,
                               islem_yapan_sicil: str) -> dict:
    conn = cursor = None
    try:
        conn   = db_baglan()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT firma_adi, durum FROM firma WHERE firma_kodu=%s", (firma_kodu,)
        )
        satir = cursor.fetchone()
        if not satir:
            return {"icerik": {"detail": "Firma bulunamadı."}, "statu": 404}

        firma_adi, eski_durum = satir
        if eski_durum == yeni_durum:
            return {"icerik": {"detail": "Durum zaten bu değerde."}, "statu": 400}

        cursor.execute(
            """UPDATE firma
               SET durum=%s, olusturma_guncelleme_zamani=NOW(), olusturan_guncelleyen_sicil=%s
               WHERE firma_kodu=%s""",
            (yeni_durum, islem_yapan_sicil, firma_kodu)
        )
        cursor.execute(
            """INSERT INTO firma_guncelleme_loglari
               (firma_kodu, firma_adi, eski_durum, yeni_durum, islem_yapan_kullanici_sicil)
               VALUES (%s, %s, %s, %s, %s)""",
            (firma_kodu, firma_adi, eski_durum, yeni_durum, islem_yapan_sicil)
        )
        conn.commit()
        durum_yazi = "aktifleştirildi" if yeni_durum else "pasife alındı"
        return {"icerik": {"mesaj": f"Firma {durum_yazi}."}, "statu": 200}
    except Exception as e:
        print(f"[firma_servisi] durum {type(e).__name__}: {e}", file=sys.stderr)
        if conn: conn.rollback()
        return {"icerik": {"detail": "Durum güncellenemedi."}, "statu": 500}
    finally:
        if cursor: cursor.close()
        if conn:   conn.close()