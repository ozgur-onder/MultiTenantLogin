import os
import hashlib
from fastapi import APIRouter, Form, HTTPException
from fastapi.responses import JSONResponse
import psycopg2

router = APIRouter()

def veritabani_baglantisi():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        port=os.getenv("DB_PORT", "5432")
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

        # Güvenlik Kontrolü: Zaten kullanıcı varsa reddet
        cursor.execute("SELECT COUNT(*) FROM kullanicilar;")
        if cursor.fetchone()[0] > 0:
            cursor.close()
            raise HTTPException(status_code=403, detail="Sistem kurulumu daha önce tamamlanmıştır!")

        # Yönetici şifresi SHA-256 ile hashleniyor
        sifre_hash = hashlib.sha256(sifre.encode('utf-8')).hexdigest()

        # 1. İlk Yöneticinin Kaydı
        cursor.execute("""
            INSERT INTO kullanicilar (sicil, ad, soyad, email, parola, olusturan_kullanici_sicil)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (sicil_no, ad, soyad, email, sifre_hash, sicil_no))

        # 2. Firma ID ve Rol ID'yi Alma (F001 ve Sistem Yöneticisi)
        cursor.execute("SELECT id FROM firma WHERE firma_kodu = 'F001';")
        firma_id = cursor.fetchone()[0]

        cursor.execute("SELECT id FROM roller WHERE rol_kodu = 1;")
        rol_id = cursor.fetchone()[0]

        # 3. Kullanıcı Yetkileri Tablosuna Kayıt
        cursor.execute("""
            INSERT INTO kullanici_yetkileri (sicil, firma_id, rol_id, tanimlayan_kullanici_sicil, durum)
            VALUES (%s, %s, %s, %s, TRUE)
        """, (sicil_no, firma_id, rol_id, sicil_no))

        # 4. SMTP Ayarları Kaydı (rapor_kodu otomatik '1' olarak ayarlandı ve ID alındı)
        cursor.execute("""
            INSERT INTO smtp_ayarlari (firma_kodu, rol_id, rapor_kodu, sunucu, port, kullanici_adi, sifre, gonderici_adi, varsayilan_mi, olusturan_guncelleyen_sicil)
            VALUES ('F001', %s, '1', %s, %s, %s, %s, %s, TRUE, %s)
            RETURNING id;
        """, (rol_id, smtp_sunucu, smtp_port, smtp_email, smtp_sifre, smtp_gonderici, sicil_no))
        
        smtp_ayar_id = cursor.fetchone()[0]

        # 5. SMTP Log Tablosuna Veri Basma
        cursor.execute("""
            INSERT INTO smtp_ayarlari_loglari (smtp_ayar_id, islem_turu, yeni_sunucu, yeni_kullanici_adi, islem_yapan_kullanici_sicil)
            VALUES (%s, 'KURULUM_EKLENDI', %s, %s, %s)
        """, (smtp_ayar_id, smtp_sunucu, smtp_email, sicil_no))

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