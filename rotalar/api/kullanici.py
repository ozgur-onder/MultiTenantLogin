import sys
import psycopg2, os
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from rotalar.yetki_servisi import oturum_gerektir

router = APIRouter(prefix="/api")

def db_baglan():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"), database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"), password=os.getenv("DB_PASS"),
        port=os.getenv("DB_PORT", "5432")
    )

@router.get("/ben")
async def beni_al(kullanici: dict = Depends(oturum_gerektir)):
    """Oturumdaki kullanıcının bilgilerini ve rol listesini döndürür."""
    conn = cursor = None
    try:
        conn   = db_baglan()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT DISTINCT rol_id FROM kullanici_yetkileri WHERE sicil=%s AND durum=TRUE",
            (kullanici["sicil"],)
        )
        roller = [r[0] for r in cursor.fetchall()]
        return JSONResponse(content={
            "sicil":    kullanici["sicil"],
            "ad_soyad": kullanici["ad_soyad"],
            "email":    kullanici["email"],
            "roller":   roller
        })
    except Exception as e:
        print(f"[kullanici] {type(e).__name__}: {e}", file=sys.stderr)
        return JSONResponse(content={"detail": "Kullanıcı bilgisi alınamadı."}, status_code=500)
    finally:
        if cursor: cursor.close()
        if conn:   conn.close()

@router.get("/profil")
async def profil_al(kullanici: dict = Depends(oturum_gerektir)):
    """Arayüzdeki sol menü ve anasayfa için profil bilgilerini döndürür."""
    conn = cursor = None
    try:
        conn   = db_baglan()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT rol_id FROM kullanici_yetkileri WHERE sicil=%s AND durum=TRUE LIMIT 1",
            (kullanici["sicil"],)
        )
        rol_kayit = cursor.fetchone()
        rol = rol_kayit[0] if rol_kayit else "Kullanıcı"
        
        return JSONResponse(content={
            "ad_soyad": kullanici["ad_soyad"],
            "rol": rol
        })
    except Exception as e:
        print(f"[profil] {type(e).__name__}: {e}", file=sys.stderr)
        return JSONResponse(content={
            "ad_soyad": kullanici.get("ad_soyad", "Bilinmeyen Kullanıcı"),
            "rol": "Belirtilmemiş"
        })
    finally:
        if cursor: cursor.close()
        if conn:   conn.close()