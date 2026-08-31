(function () {
    async function profilYukle() {
        const icerikAlani = document.getElementById("sayfa-icerik");
        if (!icerikAlani) return;

        icerikAlani.innerHTML = `
            <div style="padding: 2rem;">
                <h2>Profilim</h2>
                <p>Bilgileriniz yükleniyor...</p>
            </div>
        `;

        try {
            const yanit = await fetch("/api/profil");
            if (yanit.ok) {
                const kullanici = await yanit.json();
                icerikAlani.innerHTML = `
                    <div style="padding: 2rem;">
                        <h2 style="margin-bottom: 20px;">Profil Bilgilerim</h2>
                        <div style="padding: 20px; border-radius: 8px; background: rgba(0,0,0,0.1);">
                            <p style="margin-bottom: 10px;"><strong>Ad Soyad:</strong> ${kullanici.ad_soyad || "Belirtilmemiş"}</p>
                            <p style="margin-bottom: 10px;"><strong>Rol:</strong> ${kullanici.rol || "Belirtilmemiş"}</p>
                        </div>
                    </div>
                `;
            } else {
                icerikAlani.innerHTML = `
                    <div style="padding: 2rem;">
                        <h2>Profilim</h2>
                        <p>Bilgiler alınamadı.</p>
                    </div>
                `;
            }
        } catch (hata) {
            icerikAlani.innerHTML = `
                <div style="padding: 2rem;">
                    <h2>Profilim</h2>
                    <p>Bağlantı hatası oluştu.</p>
                </div>
            `;
        }
    }

    document.addEventListener("DOMContentLoaded", () => {
        const profilButonu = document.querySelector('[data-sayfa="profilim"]');
        if (profilButonu) {
            profilButonu.addEventListener("click", profilYukle);
        }
    });
})();