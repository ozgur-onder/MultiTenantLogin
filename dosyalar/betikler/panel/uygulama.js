document.addEventListener("DOMContentLoaded", function () {
    // ID'yi HTML'deki "cikis-btn" ile eşitledik
    const cikisButonu = document.getElementById("cikis-btn");

    if (cikisButonu) {
        cikisButonu.addEventListener("click", async function (e) {
            e.preventDefault();

            try {
                const istek = await fetch("/cikis-yap", {
                    method: "POST"
                });

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
});