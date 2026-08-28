document.addEventListener("DOMContentLoaded", function () {
    const sifirlaBtn  = document.getElementById("sifirlaBtn");
    const sicilKutusu = document.getElementById("sicil-no");
    const epostaKutusu = document.getElementById("email");

    if (!sifirlaBtn) return;

    sifirlaBtn.addEventListener("click", async function (event) {
        event.preventDefault();

        const sicil  = sicilKutusu.value.trim();
        const eposta = epostaKutusu.value.trim();

        if (!sicil || !eposta) {
            bildirimGoster("Lütfen sicil numarası ve e-posta adresinizi girin.", "uyari");
            return;
        }

        const orjinalYazi    = sifirlaBtn.innerText;
        sifirlaBtn.innerText = "Gönderiliyor...";
        sifirlaBtn.disabled  = true;

        const formVerisi = new FormData();
        formVerisi.append("sicil",  sicil);
        formVerisi.append("email",  eposta);

        try {
            const istek = await fetch("/sifre-sifirlama-talep", {
                method: "POST",
                body:   formVerisi
            });

            const cevap = await istek.json();

            if (istek.ok) {
                bildirimGoster(cevap.mesaj, "basari", 3);
                sicilKutusu.value  = "";
                epostaKutusu.value = "";
                setTimeout(() => { window.location.href = "/"; }, 2500);
            } else {
                bildirimGoster(cevap.detail || "Bir hata oluştu, lütfen tekrar deneyin.", "hata");
            }
        } catch {
            bildirimGoster("Sunucuya ulaşılamıyor. Lütfen bağlantınızı kontrol edin.", "hata");
        } finally {
            sifirlaBtn.innerText = orjinalYazi;
            sifirlaBtn.disabled  = false;
        }
    });
});