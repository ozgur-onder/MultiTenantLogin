document.addEventListener("DOMContentLoaded", function () {

    const urlParams = new URLSearchParams(window.location.search);
    const token     = urlParams.get("token");

    if (!token) {
        bildirimGoster("Geçersiz bağlantı. Lütfen şifre sıfırlama işlemini yeniden başlatın.", "hata", 0);
        setTimeout(() => { window.location.href = "/sayfalar/sifremi_unuttum"; }, 2500);
        return;
    }

    const yenileBtn     = document.getElementById("yenileBtn");
    const yeniSifreEl   = document.getElementById("yeni-sifre");
    const sifreTekrarEl = document.getElementById("sifre-tekrar");

    const KARMASIKLIK = /^(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#$%^&*(),.?":{}|<>]).{12,}$/;

    if (!yenileBtn) return;

    yenileBtn.addEventListener("click", async function (event) {
        event.preventDefault();

        const yeniSifre   = yeniSifreEl.value;
        const sifreTekrar = sifreTekrarEl.value;

        if (!yeniSifre || !sifreTekrar) {
            bildirimGoster("Lütfen tüm alanları doldurun.", "uyari");
            return;
        }
        if (yeniSifre !== sifreTekrar) {
            bildirimGoster("Girdiğiniz şifreler eşleşmiyor. Lütfen tekrar deneyin.", "hata");
            sifreTekrarEl.value = "";
            sifreTekrarEl.focus();
            return;
        }
        if (!KARMASIKLIK.test(yeniSifre)) {
            bildirimGoster(
                "Şifre kuralları: en az 12 karakter, büyük harf, küçük harf ve özel karakter (ör: !) içermelidir.",
                "uyari", 6
            );
            return;
        }

        const orjinalYazi   = yenileBtn.innerText;
        yenileBtn.innerText = "Güncelleniyor...";
        yenileBtn.disabled  = true;

        const formVerisi = new FormData();
        formVerisi.append("token",      token);
        formVerisi.append("yeni_sifre", yeniSifre);

        try {
            const istek = await fetch("/sifre-yenile-islem", {
                method: "POST",
                body:   formVerisi
            });

            const cevap = await istek.json();

            if (istek.ok) {
                bildirimGoster(cevap.mesaj || "Şifreniz başarıyla güncellendi.", "basari", 3);
                setTimeout(() => { window.location.href = "/"; }, 2500);
            } else {
                const mesaj = cevap.detail || "Bir hata oluştu, lütfen tekrar deneyin.";
                bildirimGoster(mesaj, "hata");
                if (mesaj.toLowerCase().includes("geçersiz") || mesaj.toLowerCase().includes("dolmuş")) {
                    setTimeout(() => { window.location.href = "/sayfalar/sifremi_unuttum"; }, 3000);
                }
            }
        } catch {
            bildirimGoster("Sunucuya ulaşılamıyor. Lütfen bağlantınızı kontrol edin.", "hata");
        } finally {
            yenileBtn.innerText = orjinalYazi;
            yenileBtn.disabled  = false;
        }
    });
});