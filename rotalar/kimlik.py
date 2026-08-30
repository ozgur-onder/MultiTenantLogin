from fastapi import APIRouter, Form, Request
from fastapi.responses import JSONResponse, RedirectResponse

from rotalar.giris_servisi import giris_yap as giris_yap_islem
from rotalar.oturum_servisi import oturum_sonlandir, OTURUM_CEREZ
from rotalar.sifre_servisi  import sifre_sifirlama_islemini_yap, yeni_sifreyi_kaydet

router = APIRouter()

# ── Giriş ─────────────────────────────────────────────────────────────────────
@router.post("/giris-yap")
async def giris_yap(
    request: Request,
    eposta: str = Form(...),
    sifre:  str = Form(...)
):
    sonuc = await giris_yap_islem(request, eposta, sifre)

    cevap = JSONResponse(content=sonuc["icerik"], status_code=sonuc["statu"])

    if sonuc["statu"] == 200:
        cevap.set_cookie(
            key      = OTURUM_CEREZ,
            value    = sonuc["token"],
            httponly = True,
            samesite = "lax",
            max_age  = 60 * 60 * 8   # 8 saat
        )

    return cevap

# ── Çıkış ─────────────────────────────────────────────────────────────────────
@router.post("/cikis-yap")
async def cikis_yap(request: Request):
    token = request.cookies.get(OTURUM_CEREZ)
    await oturum_sonlandir(token)

    cevap = JSONResponse(
        content    = {"mesaj": "Oturum kapatıldı."},
        status_code= 200
    )
    cevap.delete_cookie(OTURUM_CEREZ)
    return cevap

# ── Şifre sıfırlama (değişmedi) ───────────────────────────────────────────────
@router.post("/sifre-sifirlama-talep")
async def sifre_sifirlama(
    request: Request,
    sicil:  str = Form(...),
    email:  str = Form(...)
):
    if not sicil or not email:
        return JSONResponse(content={"detail": "Bilgiler eksik."}, status_code=400)

    sonuc = await sifre_sifirlama_islemini_yap(request, sicil, email)
    cevap = JSONResponse(content=sonuc["icerik"], status_code=sonuc["statu"])

    if "cerez_ekle" in sonuc:
        cevap.set_cookie(**sonuc["cerez_ekle"])
    elif "cerez_sil" in sonuc:
        cevap.delete_cookie(sonuc["cerez_sil"])

    return cevap

@router.post("/sifre-yenile-islem")
async def sifre_yenile(
    token:      str = Form(...),
    yeni_sifre: str = Form(...)
):
    if not token or not yeni_sifre:
        return JSONResponse(content={"detail": "Eksik bilgi gönderildi."}, status_code=400)

    sonuc = await yeni_sifreyi_kaydet(token, yeni_sifre)
    return JSONResponse(content=sonuc["icerik"], status_code=sonuc["statu"])