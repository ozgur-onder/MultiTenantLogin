from fastapi import APIRouter, Form
from fastapi.responses import JSONResponse

router = APIRouter()

@router.post("/giris-yap")
async def giris_yap(eposta: str = Form(...), sifre: str = Form(...)):
    # İleride burada veritabanından e-posta ve şifre kontrolü yapacağız
    if eposta and sifre:
        return JSONResponse(
            content={"mesaj": "Giriş başarılı, yönlendiriliyorsunuz... (Demo)"}, 
            status_code=200
        )
    return JSONResponse(
        content={"mesaj": "E-posta veya şifre eksik."}, 
        status_code=400
    )

@router.post("/sifre-sifirlama-talep")
async def sifre_sifirlama(sicil: str = Form(...), email: str = Form(...)):
    # İleride burada veritabanından sicil ve e-posta eşleşmesini kontrol edeceğiz
    if sicil and email:
        return JSONResponse(
            content={"mesaj": "Şifre sıfırlama bağlantısı e-posta adresinize gönderildi."}, 
            status_code=200
        )
    else:
        return JSONResponse(
            content={"mesaj": "Bilgiler eksik veya hatalı."}, 
            status_code=400
        )