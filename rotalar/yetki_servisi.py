import sys
from fastapi import Request, HTTPException
from rotalar.oturum_servisi import oturum_dogrula
import psycopg2
import os

def db_baglan():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"), database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"), password=os.getenv("DB_PASS"),
        port=os.getenv("DB_PORT", "5432")
    )

OTURUM_CEREZ = "oturum_token"

async def oturum_gerektir(request: Request) -> dict:
    """
    FastAPI dependency — geçerli oturum yoksa 401 fırlatır.
    Geçerliyse kullanıcı bilgilerini döndürür.
    """
    token = request.cookies.get(OTURUM_CEREZ)
    kullanici = await oturum_dogrula(token)
    if not kullanici:
        raise HTTPException(status_code=401, detail="Oturum bulunamadı veya süresi doldu.")
    return kullanici

async def rol_gerektir(sicil: str, rol_id: int) -> bool:
    """
    Kullanıcının belirtilen rol_id'ye sahip aktif yetkisi var mı kontrol eder.
    Herhangi bir firmada bu role sahipse True döner.
    """
    conn = cursor = None
    try:
        conn   = db_baglan()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT 1 FROM kullanici_yetkileri
               WHERE sicil = %s AND rol_id = %s AND durum = TRUE
               LIMIT 1""",
            (sicil, rol_id)
        )
        return cursor.fetchone() is not None
    except Exception as e:
        print(f"[yetki_servisi] {type(e).__name__}: {e}", file=sys.stderr)
        return False
    finally:
        if cursor: cursor.close()
        if conn:   conn.close()

async def super_admin_gerektir(request: Request) -> dict:
    """
    FastAPI dependency — rol_id=1 (Sistem Yöneticisi) yetkisi yoksa 403 fırlatır.
    """
    token    = request.cookies.get(OTURUM_CEREZ)
    kullanici = await oturum_dogrula(token)
    if not kullanici:
        raise HTTPException(status_code=401, detail="Oturum bulunamadı veya süresi doldu.")
    if not await rol_gerektir(kullanici["sicil"], rol_id=1):
        raise HTTPException(status_code=403, detail="Bu işlem için yetkiniz bulunmuyor.")
    return kullanici