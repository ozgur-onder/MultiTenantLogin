import os
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import psycopg2

router = APIRouter()

ANA_DIZIN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sayfalar = Jinja2Templates(directory=os.path.join(ANA_DIZIN, "dosyalar", "iskeletler"))

def kullanici_var_mi():
    """Veritabanı kullanicilar tablosunda kayıt olup olmadığını kontrol eder."""
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "db"), # Docker içinde servis adı 'db' olacak
            database=os.getenv("DB_NAME", "bi_veritabani"),
            user=os.getenv("DB_USER", "ozgur.onder"),
            password=os.getenv("DB_PASS", "BZrf5399!"),
            port=os.getenv("DB_PORT", "5432")
        )
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM kullanicilar;")
        sayi = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return sayi > 0
    except Exception:
        # Veritabanı henüz ayağa kalkmadıysa veya tablolar oluşmadıysa kurulum açık kalabilir
        return False

@router.get("/", response_class=HTMLResponse)
async def anasayfa(request: Request):
    # Eğer hiç kullanıcı yoksa, direkt kurulum sayfasına yönlendir
    if not kullanici_var_mi():
        return RedirectResponse(url="/sayfalar/kurulum", status_code=303)
    return sayfalar.TemplateResponse(request=request, name="giris.html", context={"request": request})

@router.get("/sayfalar/sifremi_unuttum", response_class=HTMLResponse)
async def sifremi_unuttum(request: Request):
    return sayfalar.TemplateResponse(request=request, name="sifremi_unuttum.html", context={"request": request})

@router.get("/sayfalar/kurulum", response_class=HTMLResponse)
async def kurulum(request: Request):
    # Zaten kullanıcı varsa kurulum sayfası KESİNLİKLE açılamaz, ana sayfaya atar
    if kullanici_var_mi():
        return RedirectResponse(url="/", status_code=303)
    return sayfalar.TemplateResponse(request=request, name="kurulum.html", context={"request": request})