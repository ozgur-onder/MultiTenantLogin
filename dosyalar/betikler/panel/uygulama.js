document.addEventListener("DOMContentLoaded", async function () {
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

    const isimAlani = document.getElementById("kullanici-tam-adi");
    const rolAlani = document.getElementById("kullanici-rol");
    const avatarAlani = document.getElementById("kullanici-avatar");
    const yonetimMenusu = document.getElementById("yonetim-bolum");

    try {
        const yanit = await fetch("/api/profil"); 
        if (yanit.ok) {
            const kullanici = await yanit.json();
            
            // 1. Sadece ad soyad gösterilir, rol ID'si gizlenir
            isimAlani.textContent = kullanici.ad_soyad || "İsimsiz Kullanıcı";
            if(rolAlani) rolAlani.textContent = ""; 
            
            if (kullanici.ad_soyad) {
                const harfler = kullanici.ad_soyad.split(" ")
                    .map(kelime => kelime.charAt(0))
                    .join("")
                    .substring(0, 2)
                    .toUpperCase();
                avatarAlani.textContent = harfler;
            }

            // 2. Rol kontrolü: Yönetim menüsünün görünürlüğünü yetkiye göre açarız
            // Kendi veritabanınızdaki yetkili rol numaralarını/isimlerini bu diziye ekleyebilirsiniz
            const yetkiliRoller = ["Takım Lideri", "Yönetici", 1, "1"];
            if (yonetimMenusu && kullanici.rol && yetkiliRoller.includes(kullanici.rol)) {
                yonetimMenusu.removeAttribute("hidden");
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