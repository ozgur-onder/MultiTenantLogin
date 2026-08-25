import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn

# Rotaları içeri aktarıyoruz
from rotalar import sayfalar, kimlik, kurulum

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = FastAPI(title="İş Zekası Platformu API")

# Statik dosyaları (CSS, JS) uygulamaya tanıtıyoruz
app.mount("/dosyalar", StaticFiles(directory=os.path.join(BASE_DIR, "dosyalar")), name="dosyalar")
app.mount("/temalar", StaticFiles(directory=os.path.join(BASE_DIR, "dosyalar", "temalar")), name="temalar")

# Rotaları ana uygulamaya bağlıyoruz
app.include_router(sayfalar.router)
app.include_router(kimlik.router)
app.include_router(kurulum.router)

if __name__ == "__main__":
    uvicorn.run("sunucu:app", host="0.0.0.0", port=5000, reload=True)