document.addEventListener("DOMContentLoaded", function () {
    const girisButonu = document.getElementById("loginBtn");
    const epostaKutusu = document.getElementById("kullanici_adi");
    const sifreKutusu = document.getElementById("password");

    girisButonu.addEventListener("click", async function () {
        const eposta = epostaKutusu.value.trim();
        const sifre = sifreKutusu.value;

        if (!eposta || !sifre) {
            alert("Lütfen e-posta ve şifrenizi girin.");
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
                alert(cevap.mesaj);
                // Başarılı girişten sonra panele yönlendirme komutu eklendi
                setTimeout(() => {
                    window.location.href = "/panel";
                }, 1000);
            } else {
                alert(cevap.detail || cevap.mesaj || "Giriş işlemi başarısız.");
            }
        } catch (hata) {
            alert("Sunucuya bağlanırken bir sorun oluştu.");
        } finally {
            girisButonu.innerText = "Giriş Yap";
            girisButonu.disabled = false;
        }
    });
});