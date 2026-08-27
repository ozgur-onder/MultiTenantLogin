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
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS"),
            port=os.getenv("DB_PORT", "5432")
        )
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM kullanicilar;")
        sayi = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return sayi > 0
    except Exception:
        return False

@router.get("/", response_class=HTMLResponse)
async def anasayfa(request: Request):
    if not kullanici_var_mi():
        return RedirectResponse(url="/sayfalar/kurulum", status_code=303)
    return sayfalar.TemplateResponse(request=request, name="giris.html", context={"request": request})

@router.get("/sayfalar/sifremi_unuttum", response_class=HTMLResponse)
async def sifremi_unuttum(request: Request):
    return sayfalar.TemplateResponse(request=request, name="sifremi_unuttum.html", context={"request": request})

@router.get("/sayfalar/sifre_yenile", response_class=HTMLResponse)
async def sifre_yenile(request: Request, token: str = None):
    # Token yoksa şifremi unuttum sayfasına yönlendir
    if not token:
        return RedirectResponse(url="/sayfalar/sifremi_unuttum", status_code=303)
    return sayfalar.TemplateResponse(
        request=request,
        name="sifre_yenile.html",
        context={"request": request, "token": token}
    )

@router.get("/sayfalar/kurulum", response_class=HTMLResponse)
async def kurulum(request: Request):
    if kullanici_var_mi():
        return RedirectResponse(url="/", status_code=303)
    return sayfalar.TemplateResponse(request=request, name="kurulum.html", context={"request": request})