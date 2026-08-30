import sys
import psycopg2, os

def db_baglan():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"), database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"), password=os.getenv("DB_PASS"),
        port=os.getenv("DB_PORT", "5432")
    )

async def rol_listesi() -> dict:
    conn = cursor = None
    try:
        conn   = db_baglan()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT rol_kodu, rol_adi, durum, olusturma_guncelleme_zamani FROM roller ORDER BY rol_kodu"
        )
        roller = [
            {"rol_kodu": r[0], "rol_adi": r[1],
             "durum": r[2], "zaman": r[3].isoformat()}
            for r in cursor.fetchall()
        ]
        return {"icerik": roller, "statu": 200}
    except Exception as e:
        print(f"[rol_servisi] listele {type(e).__name__}: {e}", file=sys.stderr)
        return {"icerik": {"detail": "Roller alınamadı."}, "statu": 500}
    finally:
        if cursor: cursor.close()
        if conn:   conn.close()

async def rol_ekle(rol_kodu: int, rol_adi: str, islem_yapan_sicil: str) -> dict:
    conn = cursor = None
    try:
        conn   = db_baglan()
        cursor = conn.cursor()

        cursor.execute("SELECT 1 FROM roller WHERE rol_kodu=%s", (rol_kodu,))
        if cursor.fetchone():
            return {"icerik": {"detail": "Bu rol kodu zaten kayıtlı."}, "statu": 409}

        cursor.execute(
            """INSERT INTO roller (rol_kodu, rol_adi, olusturan_guncelleyen_sicil)
               VALUES (%s, %s, %s)""",
            (rol_kodu, rol_adi, islem_yapan_sicil)
        )
        conn.commit()
        return {"icerik": {"mesaj": "Rol başarıyla eklendi."}, "statu": 201}
    except Exception as e:
        print(f"[rol_servisi] ekle {type(e).__name__}: {e}", file=sys.stderr)
        if conn: conn.rollback()
        return {"icerik": {"detail": "Rol eklenemedi."}, "statu": 500}
    finally:
        if cursor: cursor.close()
        if conn:   conn.close()

async def rol_durum_guncelle(rol_kodu: int, yeni_durum: bool,
                             islem_yapan_sicil: str) -> dict:
    conn = cursor = None
    try:
        conn   = db_baglan()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT rol_adi, durum FROM roller WHERE rol_kodu=%s", (rol_kodu,)
        )
        satir = cursor.fetchone()
        if not satir:
            return {"icerik": {"detail": "Rol bulunamadı."}, "statu": 404}

        rol_adi, eski_durum = satir
        if eski_durum == yeni_durum:
            return {"icerik": {"detail": "Durum zaten bu değerde."}, "statu": 400}

        cursor.execute(
            """UPDATE roller
               SET durum=%s, olusturma_guncelleme_zamani=NOW(), olusturan_guncelleyen_sicil=%s
               WHERE rol_kodu=%s""",
            (yeni_durum, islem_yapan_sicil, rol_kodu)
        )
        cursor.execute(
            """INSERT INTO rol_guncelleme_loglari
               (rol_kodu, rol_adi, eski_durum, yeni_durum, islem_yapan_kullanici_sicil)
               VALUES (%s, %s, %s, %s, %s)""",
            (str(rol_kodu), rol_adi, eski_durum, yeni_durum, islem_yapan_sicil)
        )
        conn.commit()
        durum_yazi = "aktifleştirildi" if yeni_durum else "pasife alındı"
        return {"icerik": {"mesaj": f"Rol {durum_yazi}."}, "statu": 200}
    except Exception as e:
        print(f"[rol_servisi] durum {type(e).__name__}: {e}", file=sys.stderr)
        if conn: conn.rollback()
        return {"icerik": {"detail": "Durum güncellenemedi."}, "statu": 500}
    finally:
        if cursor: cursor.close()
        if conn:   conn.close()