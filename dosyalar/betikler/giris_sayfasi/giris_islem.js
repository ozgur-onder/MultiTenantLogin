document.addEventListener("DOMContentLoaded", function () {
    const girisButonu = document.getElementById("loginBtn");
    const epostaKutusu = document.getElementById("kullanici_adi");
    const sifreKutusu = document.getElementById("password");

    function hataPenceresiGoster(mesaj) {
        const overlay = document.createElement("div");
        overlay.className = "hata-modal-arkaplan";

        const modal = document.createElement("div");
        modal.className = "hata-modal-kutu";

        const iconDiv = document.createElement("div");
        iconDiv.className = "hata-modal-ikon";
        iconDiv.innerHTML = '<svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#ef4444" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line></svg>';

        const title = document.createElement("h3");
        title.className = "hata-modal-baslik";
        title.innerText = "Hata";

        const desc = document.createElement("p");
        desc.className = "hata-modal-metin";
        desc.innerText = mesaj;

        const btn = document.createElement("button");
        btn.className = "hata-modal-buton";
        btn.innerText = "Anladım";

        btn.onclick = function() {
            document.body.removeChild(overlay);
        };

        modal.appendChild(iconDiv);
        modal.appendChild(title);
        modal.appendChild(desc);
        modal.appendChild(btn);
        overlay.appendChild(modal);
        document.body.appendChild(overlay);
    }

    girisButonu.addEventListener("click", async function (e) {
        e.preventDefault();
        
        const eposta = epostaKutusu.value.trim();
        const sifre = sifreKutusu.value;

        if (!eposta || !sifre) {
            hataPenceresiGoster("Lütfen e-posta ve şifrenizi girin.");
            return;
        }

        girisButonu.innerText = "Bekleyiniz...";
        girisButonu.disabled = true;

        const formVerisi = new FormData();
        formVerisi.append("eposta", eposta);
        formVerisi.append("sifre", sifre);

        try {
            const istek = await fetch("/giris-yap", {
                method: "POST",
                body: formVerisi
            });

            const cevap = await istek.json();

            if (istek.ok) {
                window.location.href = "/panel";
            } else {
                hataPenceresiGoster(cevap.detail || cevap.mesaj || "Giriş işlemi başarısız.");
                girisButonu.innerText = "Giriş Yap";
                girisButonu.disabled = false;
            }
        } catch (hata) {
            hataPenceresiGoster("Sunucuya bağlanırken bir sorun oluştu.");
            girisButonu.innerText = "Giriş Yap";
            girisButonu.disabled = false;
        }
    });
});