import os
import hashlib
from fastapi import APIRouter, Form, HTTPException
from fastapi.responses import JSONResponse
import psycopg2

router = APIRouter()

DB_HOST = os.getenv("DB_HOST", "db")
DB_NAME = os.getenv("DB_NAME", "bi_veritabani")
DB_USER = os.getenv("DB_USER", "ozgur.onder")
DB_PASS = os.getenv("DB_PASS", "BZrf5399!")
DB_PORT = os.getenv("DB_PORT", "5432")

def veritabani_baglantisi():
    return psycopg2.connect(
        host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS, port=DB_PORT
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
    smtp_gonderici: str = Form(...)
):
    conn = None
    try:
        conn = veritabani_baglantisi()
        cursor = conn.cursor()

        # GÜVENLİK KONTROLÜ: Tabloda zaten kullanıcı varsa kurulumu reddet!
        cursor.execute("SELECT COUNT(*) FROM kullanicilar;")
        if cursor.fetchone()[0] > 0:
            cursor.close()
            raise HTTPException(status_code=403, detail="Sistem kurulumu daha önce tamamlanmıştır!")

        sifre_hash = hashlib.sha256(sifre.encode('utf-8')).hexdigest()

        # 1. İlk Yöneticinin Kaydı (init.sql tablo yapısına birebir uygun)
        cursor.execute("""
            INSERT INTO kullanicilar (sicil, ad, soyad, email, parola, olusturan_kullanici_sicil)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (sicil_no, ad, soyad, email, sifre_hash, sicil_no))

        # 2. Firma ID'sini ve Rol ID'sini Bulma (init.sql ile gelen F001 ve Sistem Yöneticisi)
        cursor.execute("SELECT id FROM firma WHERE firma_kodu = 'F001';")
        firma_id = cursor.fetchone()[0]

        cursor.execute("SELECT id FROM roller WHERE rol_kodu = 1;")
        rol_id = cursor.fetchone()[0]

        # 3. Kullanıcı Yetkileri Tablosuna İlişkinin Eklenmesi
        cursor.execute("""
            INSERT INTO kullanici_yetkileri (sicil, firma_id, rol_id, tanimlayan_kullanici_sicil, durum)
            VALUES (%s, %s, %s, %s, TRUE)
        """, (sicil_no, firma_id, rol_id, sicil_no))

        # 4. SMTP Ayarlarının Kaydı (Firma kodu ve Rol ID ile)
        cursor.execute("""
            INSERT INTO smtp_ayarlari (firma_kodu, rol_id, sunucu, port, kullanici_adi, sifre, gonderici_adi, varsayilan_mi, olusturan_guncelleyen_sicil)
            VALUES ('F001', %s, %s, %s, %s, %s, %s, TRUE, %s)
        """, (rol_id, smtp_sunucu, smtp_port, smtp_email, smtp_sifre, smtp_gonderici, sicil_no))

        conn.commit()
        cursor.close()

        return JSONResponse(
            content={"mesaj": "Sistem kurulumu başarıyla tamamlandı! Yönlendiriliyorsunuz..."}, 
            status_code=200
        )

    except HTTPException as he:
        raise he
    except Exception as e:
        if conn:
            conn.rollback()
        raise HTTPException(status_code=500, detail=f"Veritabanı kayıt hatası: {str(e)}")
    finally:
        if conn:
            conn.close()