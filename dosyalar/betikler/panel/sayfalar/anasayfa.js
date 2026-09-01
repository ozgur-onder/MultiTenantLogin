(function () {
    async function anasayfaYukle() {
        const icerikAlani = document.getElementById("sayfa-icerik");
        if (!icerikAlani) return;

        let adSoyad = "Kullanıcı"; 

        try {
            const yanit = await fetch("/api/profil");
            if (yanit.ok) {
                const kullanici = await yanit.json();
                if (kullanici.ad_soyad) {
                    adSoyad = kullanici.ad_soyad;
                }
            }
        } catch (hata) {
            // Veri çekilemezse varsayılan isim kullanılır
        }

        icerikAlani.innerHTML = `
            <div style="padding: 2rem;">
                <h2 style="margin-bottom: 10px;">Hoşgeldin ${adSoyad},</h2>
                <p style="opacity: 0.8;">
                    Sol menüyü kullanarak işlemlerinize başlayabilir, verilerinizi analiz edebilirsiniz.
                </p>
            </div>
        `;
    }

    document.addEventListener("DOMContentLoaded", () => {
        anasayfaYukle();
        
        const anasayfaButonu = document.querySelector('[data-sayfa="anasayfa"]');
        if (anasayfaButonu) {
            anasayfaButonu.addEventListener("click", anasayfaYukle);
        }
    });
})();