document.addEventListener("DOMContentLoaded", function () {
    // Tema Ayarları ve İkonlar
    const temaStili = document.getElementById("theme-style");
    const temaButonu = document.querySelector(".theme-toggle");

    const ayIkonu = '<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg>';
    const gunesIkonu = '<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line></svg>';

    function temaUygula(tema) {
        if (tema === "koyu") {
            temaStili.setAttribute("href", "/temalar/giris_sayfasi/siyah.css");
            temaButonu.innerHTML = gunesIkonu; // Koyu temada güneş ikonunu göster
        } else {
            temaStili.setAttribute("href", "/temalar/giris_sayfasi/beyaz.css");
            temaButonu.innerHTML = ayIkonu; // Açık temada ay ikonunu göster
        }
        localStorage.setItem("secilen-tema", tema);
    }

    const kayitliTema = localStorage.getItem("secilen-tema");
    if (kayitliTema) {
        temaUygula(kayitliTema);
    } else {
        temaUygula("acik");
    }

    temaButonu.addEventListener("click", function () {
        const mevcutCss = temaStili.getAttribute("href");
        if (mevcutCss.includes("beyaz.css")) {
            temaUygula("koyu");
        } else {
            temaUygula("acik");
        }
    });

    // Şifre Göster/Gizle ve İkon Değişimi
    const sifreKutusu = document.getElementById("password");
    const gosterButonu = document.getElementById("togglePasswordBtn");

    gosterButonu.addEventListener("click", function () {
        if (sifreKutusu.type === "password") {
            sifreKutusu.type = "text";
            gosterButonu.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path><line x1="1" y1="1" x2="23" y2="23"></line></svg>';
        } else {
            sifreKutusu.type = "password";
            gosterButonu.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>';
        }
    });

    // Giriş Yapma İşlemi
    const girisButonu = document.getElementById("loginBtn");
    const epostaKutusu = document.getElementById("kullanici_adi");

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
            } else {
                alert(cevap.mesaj);
            }
        } catch (hata) {
            alert("Sunucuya bağlanırken bir sorun oluştu.");
        } finally {
            girisButonu.innerText = "Giriş Yap";
            girisButonu.disabled = false;
        }
    });
});