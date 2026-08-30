import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn

from rotalar import sayfalar, kimlik, kurulum
from rotalar.api import kullanici, anasayfa, firma, rol

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = FastAPI(title="İş Zekası Platformu API", docs_url="/docs", redoc_url=None)

# ── Statik dosyalar ───────────────────────────────────────────────────────────
app.mount("/dosyalar", StaticFiles(
    directory=os.path.join(BASE_DIR, "dosyalar")), name="dosyalar"
)
app.mount("/temalar", StaticFiles(
    directory=os.path.join(BASE_DIR, "dosyalar", "temalar")), name="temalar"
)

# ── Sayfa rotaları ────────────────────────────────────────────────────────────
app.include_router(sayfalar.router)
app.include_router(kimlik.router)
app.include_router(kurulum.router)

# ── API rotaları ──────────────────────────────────────────────────────────────
app.include_router(kullanici.router)
app.include_router(anasayfa.router)
app.include_router(firma.router)
app.include_router(rol.router)

if __name__ == "__main__":
    uvicorn.run("sunucu:app", host="0.0.0.0", port=5000, reload=True)