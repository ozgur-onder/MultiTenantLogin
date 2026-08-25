import os
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()

ANA_DIZIN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sayfalar = Jinja2Templates(directory=os.path.join(ANA_DIZIN, "dosyalar", "iskeletler"))

@router.get("/", response_class=HTMLResponse)
async def anasayfa(request: Request):
    return sayfalar.TemplateResponse(request=request, name="giris.html", context={"request": request})

@router.get("/sayfalar/sifremi_unuttum", response_class=HTMLResponse)
async def sifremi_unuttum(request: Request):
    return sayfalar.TemplateResponse(request=request, name="sifremi_unuttum.html", context={"request": request})

@router.get("/sayfalar/kurulum", response_class=HTMLResponse)
async def kurulum(request: Request):
    return sayfalar.TemplateResponse(request=request, name="kurulum.html", context={"request": request})