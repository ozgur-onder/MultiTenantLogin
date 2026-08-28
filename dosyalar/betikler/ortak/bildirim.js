/**
 * bildirim.js — Modal bildirim sistemi
 * Bağımlılık: /temalar/ortak/bildirim.css yüklenmiş olmalıdır.
 *
 * bildirimGoster(mesaj, tur, sureSaniye)
 *   tur        : "basari" | "hata" | "uyari" | "bilgi"
 *   sureSaniye : 0 = yalnızca butona/overlay'e tıklamayla kapanır (varsayılan)
 *                n = n saniye sonra otomatik kapanır
 */
function bildirimGoster(mesaj, tur = "bilgi", sureSaniye = 0) {

    document.getElementById("bildirim-overlay")?.remove();

    const IKONLAR   = { basari: "✓", hata: "✕", uyari: "!", bilgi: "i" };
    const BASLIKLAR = { basari: "Başarılı", hata: "Hata", uyari: "Uyarı", bilgi: "Bilgi" };

    const overlay = document.createElement("div");
    overlay.id        = "bildirim-overlay";
    overlay.className = `bildirim-overlay bildirim--${tur}`;

    const kart = document.createElement("div");
    kart.className = "bildirim-kart";

    const ikon = document.createElement("div");
    ikon.className   = "bildirim-ikon";
    ikon.textContent = IKONLAR[tur] ?? "i";

    const baslik = document.createElement("h3");
    baslik.className   = "bildirim-baslik";
    baslik.textContent = BASLIKLAR[tur] ?? "Bilgi";

    const mesajEl = document.createElement("p");
    mesajEl.className   = "bildirim-mesaj";
    mesajEl.textContent = mesaj;

    const buton = document.createElement("button");
    buton.className   = "bildirim-buton";
    buton.textContent = "Anladım";

    kart.append(ikon, baslik, mesajEl, buton);
    overlay.appendChild(kart);
    document.body.appendChild(overlay);

    const kapat = () => {
        overlay.classList.remove("bildirim--aktif");
        setTimeout(() => overlay.remove(), 260);
    };

    buton.addEventListener("click", kapat);
    overlay.addEventListener("click", (e) => { if (e.target === overlay) kapat(); });

    requestAnimationFrame(() => overlay.classList.add("bildirim--aktif"));

    if (sureSaniye > 0) setTimeout(kapat, sureSaniye * 1000);
}