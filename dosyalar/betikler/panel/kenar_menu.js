/**
 * kenar_menu.js — Sidebar aç/kapa yönetimi
 */
(function () {
    function basla() {
        const uygulama = document.getElementById("uygulama");
        const toggleBtn = document.getElementById("menu-toggle-btn");

        if (!uygulama || !toggleBtn) return;

        // Kaydedilmiş tercihi uygula
        const kayitliDurum = localStorage.getItem("menu-durumu");
        if (kayitliDurum === "kapali") uygulama.classList.add("menu-kapali");

        toggleBtn.addEventListener("click", () => {
            uygulama.classList.toggle("menu-kapali");
            const kapali = uygulama.classList.contains("menu-kapali");
            localStorage.setItem("menu-durumu", kapali ? "kapali" : "acik");
        });
    }

    document.addEventListener("DOMContentLoaded", basla);
})();