(function () {
    function anasayfaYukle() {
        const icerikAlani = document.getElementById("sayfa-icerik");
        if (!icerikAlani) return;

        icerikAlani.innerHTML = `
            <div style="padding: 2rem;">
                <h2 style="margin-bottom: 10px;">İş Zekası Paneline Hoş Geldiniz</h2>
                <p style="opacity: 0.8;">
                    Sol menüyü kullanarak işlemlerinize başlayabilir, verilerinizi analiz edebilirsiniz.
                </p>
            </div>
        `;
    }

    document.addEventListener("DOMContentLoaded", () => {
        // Sayfa ilk açıldığında karşılama mesajını yükle
        anasayfaYukle();
        
        // Sol menüden Anasayfa'ya tıklandığında tekrar yükle
        const anasayfaButonu = document.querySelector('[data-sayfa="anasayfa"]');
        if (anasayfaButonu) {
            anasayfaButonu.addEventListener("click", anasayfaYukle);
        }
    });
})();