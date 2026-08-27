from fastapi import APIRouter, Form, Request
from fastapi.responses import JSONResponse
# İş mantığını yönetecek servisi rotalar klasöründen içe aktarıyoruz
from rotalar.sifre_servisi import sifre_sifirlama_islemini_yap, yeni_sifreyi_kaydet

router = APIRouter()

@router.post("/giris-yap")
async def giris_yap(eposta: str = Form(...), sifre: str = Form(...)):
    if eposta and sifre:
        return JSONResponse(
            content={"mesaj": "Giriş başarılı, yönlendiriliyorsunuz... (Demo)"}, 
            status_code=200
        )
    return JSONResponse(content={"detail": "E-posta veya şifre eksik."}, status_code=400)

@router.post("/sifre-sifirlama-talep")
async def sifre_sifirlama(request: Request, sicil: str = Form(...), email: str = Form(...)):
    if not sicil or not email:
        return JSONResponse(content={"detail": "Bilgiler eksik veya hatalı."}, status_code=400)
        
    sonuc = await sifre_sifirlama_islemini_yap(request, sicil, email)
    
    cevap = JSONResponse(content=sonuc["icerik"], status_code=sonuc["statu"])
    
    if "cerez_ekle" in sonuc:
        cevap.set_cookie(**sonuc["cerez_ekle"])
    elif "cerez_sil" in sonuc:
        cevap.delete_cookie(sonuc["cerez_sil"])
        
    return cevap

@router.post("/sifre-yenile-islem")
async def sifre_yenile(token: str = Form(...), yeni_sifre: str = Form(...)):
    if not token or not yeni_sifre:
        return JSONResponse(content={"detail": "Eksik bilgi gönderildi."}, status_code=400)
        
    sonuc = await yeni_sifreyi_kaydet(token, yeni_sifre)
    return JSONResponse(content=sonuc["icerik"], status_code=sonuc["statu"])