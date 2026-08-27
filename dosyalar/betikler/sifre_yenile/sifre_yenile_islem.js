document.addEventListener("DOMContentLoaded", function () {

    // Token URL'den al
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get("token");

    if (!token) {
        alert("Geçersiz bağlantı. Lütfen şifre sıfırlama işlemini yeniden başlatın.");
        window.location.href = "/sayfalar/sifremi_unuttum";
        return;
    }

    const yenileBtn     = document.getElementById("yenileBtn");
    const yeniSifreEl   = document.getElementById("yeni-sifre");
    const sifreTekrarEl = document.getElementById("sifre-tekrar");

    //Şifre karmaşıklık kuralı (backend ile aynı regex)
    const KARMASIKLIK = /^(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#$%^&*(),.?":{}|<>]).{12,}$/;

    if (yenileBtn) {
        yenileBtn.addEventListener("click", async function (event) {
            event.preventDefault();

            const yeniSifre   = yeniSifreEl.value;
            const sifreTekrar = sifreTekrarEl.value;

            // Boşluk kontrolü 
            if (!yeniSifre || !sifreTekrar) {
                alert("Lütfen tüm alanları doldurun.");
                return;
            }

            // Eşleşme kontrolü 
            if (yeniSifre !== sifreTekrar) {
                alert("Girdiğiniz şifreler eşleşmiyor. Lütfen tekrar deneyin.");
                sifreTekrarEl.value = "";
                sifreTekrarEl.focus();
                return;
            }

            // Karmaşıklık kontrolü
            if (!KARMASIKLIK.test(yeniSifre)) {
                alert(
                    "Şifre kurallarına uymuyor:\n\n" +
                    "✔ En az 12 karakter\n" +
                    "✔ En az bir büyük harf (A-Z)\n" +
                    "✔ En az bir küçük harf (a-z)\n" +
                    "✔ En az bir özel karakter (!@#$%^&* vb.)"
                );
                return;
            }

            const orjinalYazi = yenileBtn.innerText;
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
                    alert(cevap.mesaj || "Şifreniz başarıyla güncellendi.");
                    window.location.href = "/";
                } else {
                    // Token süresi dolmuş veya kullanılmış
                    const mesaj = cevap.detail || "Bir hata oluştu, lütfen tekrar deneyin.";
                    alert(mesaj);

                    // Token geçersizse sıfırlama sayfasına yönlendir
                    if (mesaj.toLowerCase().includes("geçersiz") || mesaj.toLowerCase().includes("dolmuş")) {
                        setTimeout(() => {
                            window.location.href = "/sayfalar/sifremi_unuttum";
                        }, 2000);
                    }
                }
            } catch (hata) {
                alert("Sunucuya ulaşılamıyor. Lütfen bağlantınızı kontrol edin.");
            } finally {
                yenileBtn.innerText = orjinalYazi;
                yenileBtn.disabled  = false;
            }
        });
    }
});