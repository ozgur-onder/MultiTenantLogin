document.addEventListener("DOMContentLoaded", async function () {
    // 1. Çıkış Butonu İşlemi
    const cikisButonu = document.getElementById("cikis-btn");
    if (cikisButonu) {
        cikisButonu.addEventListener("click", async function (e) {
            e.preventDefault();
            try {
                const istek = await fetch("/cikis-yap", { method: "POST" });
                if (istek.ok) {
                    window.location.href = "/";
                } else {
                    alert("Çıkış işlemi başarısız oldu.");
                }
            } catch (hata) {
                alert("Sunucuya ulaşılamıyor.");
            }
        });
    }

    // 2. Sol Menü Kullanıcı Bilgilerini Getirme
    const isimAlani = document.getElementById("kullanici-tam-adi");
    const rolAlani = document.getElementById("kullanici-rol");
    const avatarAlani = document.getElementById("kullanici-avatar");

    try {
        // Kullanıcı bilgilerini arka plandan çekiyoruz
        const yanit = await fetch("/api/profil"); 
        if (yanit.ok) {
            const kullanici = await yanit.json();
            
            isimAlani.textContent = kullanici.ad_soyad || "İsimsiz Kullanıcı";
            rolAlani.textContent = kullanici.rol || "";
            
            // İsmin baş harflerini yuvarlak avatara yazma
            if (kullanici.ad_soyad) {
                const harfler = kullanici.ad_soyad.split(" ")
                    .map(kelime => kelime.charAt(0))
                    .join("")
                    .substring(0, 2)
                    .toUpperCase();
                avatarAlani.textContent = harfler;
            }
        } else {
            isimAlani.textContent = "Bilgi Alınamadı";
            avatarAlani.textContent = "?";
        }
    } catch (hata) {
        isimAlani.textContent = "Bağlantı Sorunu";
        avatarAlani.textContent = "!";
    }
});