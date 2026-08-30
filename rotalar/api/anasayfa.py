from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from rotalar.yetki_servisi import oturum_gerektir

router = APIRouter(prefix="/api")

@router.get("/anasayfa")
async def anasayfa_verisi(kullanici: dict = Depends(oturum_gerektir)):
    """Anasayfa için karşılama verisini döndürür."""
    return JSONResponse(content={"ad_soyad": kullanici["ad_soyad"]})