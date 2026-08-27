document.addEventListener("DOMContentLoaded", function () {
    const sifirlaBtn = document.getElementById("sifirlaBtn");
    const sicilKutusu = document.getElementById("sicil-no");
    const epostaKutusu = document.getElementById("email");

    if (sifirlaBtn) {
        sifirlaBtn.addEventListener("click", async function (event) {
            event.preventDefault();

            const sicil = sicilKutusu.value.trim();
            const eposta = epostaKutusu.value.trim();

            if (!sicil || !eposta) {
                alert("Lütfen sicil numarası ve e-posta adresinizi girin.");
                return;
            }

            const orjinalYazi = sifirlaBtn.innerText;
            sifirlaBtn.innerText = "Gönderiliyor...";
            sifirlaBtn.disabled = true;

            const formVerisi = new FormData();
            formVerisi.append("sicil", sicil);
            formVerisi.append("email", eposta);

            try {
                const istek = await fetch("/sifre-sifirlama-talep", {
                    method: "POST",
                    body: formVerisi
                });

                const cevap = await istek.json();

                if (istek.ok) {
                    alert(cevap.mesaj);
                    sicilKutusu.value = '';
                    epostaKutusu.value = '';

                    setTimeout(() => {
                        window.location.href = "/";
                    }, 1500);
                } else {
                    // DÜZELTME 2: Backend hata için {"detail":"..."} döndürüyor, "mesaj" değil
                    alert(cevap.detail || "Bir hata oluştu, lütfen tekrar deneyin.");
                }
            } catch (hata) {
                alert("Sunucuya ulaşılamıyor. Lütfen bağlantınızı kontrol edin.");
            } finally {
                sifirlaBtn.innerText = orjinalYazi;
                sifirlaBtn.disabled = false;
            }
        });
    }
});