import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = FastAPI()

app.mount("/dosyalar", StaticFiles(directory=os.path.join(BASE_DIR, "dosyalar")), name="dosyalar")
app.mount("/temalar", StaticFiles(directory=os.path.join(BASE_DIR, "dosyalar", "temalar")), name="temalar")

sayfalar = Jinja2Templates(directory=os.path.join(BASE_DIR, "dosyalar", "iskeletler"))

@app.get("/", response_class=HTMLResponse)
async def anasayfa(request: Request):
    return sayfalar.TemplateResponse(request, "giris.html", {"request": request})

if __name__ == "__main__":
    uvicorn.run("sunucu:app", host="0.0.0.0", port=5000, reload=True)