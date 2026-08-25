import os
import hashlib
from fastapi import APIRouter, Form, HTTPException
from fastapi.responses import JSONResponse
import psycopg2

router = APIRouter()

# Veritabanı bağlantı ayarları (İleride .env dosyasından da çekilebilir)
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "is_zekasi_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "sifre")
DB_PORT = os.getenv("DB_PORT", "5432")

def veritabani_baglantisi():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        port=DB_PORT
    )

@router.post("/kurulum-tamamla")
async def kurulum_tamamla(
    ad: str = Form(...),
    soyad: str = Form(...),
    sicil_no: str = Form(...),
    email: str = Form(...),
    sifre: str = Form(...),
    smtp_sunucu: str = Form(...),
    smtp_port: int = Form(...),
    smtp_email: str = Form(...),
    smtp_sifre: str = Form(...),
    smtp_gonderici: str = Form(... )
):
    firma_kodu = "F001"
    rol_id = 1 
    sifre_hash = hashlib.sha256(sifre.encode('utf-8')).hexdigest()

    conn = None
    try:
        conn = veritabani_baglantisi()
        cursor = conn.cursor()

        # 1. İlk Yöneticinin Kullanıcılar Tablosuna Kaydı
        cursor.execute("""
            INSERT INTO kullanicilar (sicil, ad, soyad, email, sifre, firma_kodu, rol_id, olusturan_guncelleyen_sicil)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (sicil_no, ad, soyad, email, sifre_hash, firma_kodu, rol_id, sicil_no))

        # 2. SMTP Ayarlarının Tabloya Kaydı (F001 ve Rol ID 1 ile ilişkilendirildi)
        cursor.execute("""
            INSERT INTO smtp_ayarlari (firma_kodu, rol_id, sunucu, port, kullanici_adi, sifre, gonderici_adi, varsayilan_mi, olusturan_guncelleyen_sicil)
            VALUES (%s, %s, %s, %s, %s, %s, %s, TRUE, %s)
        """, (firma_kodu, rol_id, smtp_sunucu, smtp_port, smtp_email, smtp_sifre, smtp_gonderici, sicil_no))

        conn.commit()
        cursor.close()

        return JSONResponse(
            content={"mesaj": "Sistem kurulumu başarıyla tamamlandı! İlk yönetici ve SMTP ayarları kaydedildi."}, 
            status_code=200
        )

    except Exception as e:
        if conn:
            conn.rollback()
        raise HTTPException(
            status_code=500, 
            detail=f"Veritabanı kayıt hatası: {str(e)}"
        )
    finally:
        if conn:
            conn.close()