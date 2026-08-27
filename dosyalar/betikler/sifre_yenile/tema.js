document.addEventListener("DOMContentLoaded", function () {
    const temaStili = document.getElementById("theme-style");
    const temaButonu = document.querySelector(".theme-toggle");

    const ayIkonu = '<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg>';
    const gunesIkonu = '<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line></svg>';

    function temaUygula(tema) {
        if (tema === "koyu") {
            temaStili.setAttribute("href", "/temalar/sifremi_unuttum/siyah.css");
            temaButonu.innerHTML = gunesIkonu;
        } else {
            temaStili.setAttribute("href", "/temalar/sifremi_unuttum/beyaz.css");
            temaButonu.innerHTML = ayIkonu;
        }
        localStorage.setItem("secilen-tema", tema);
    }

    const kayitliTema = localStorage.getItem("secilen-tema");
    temaUygula(kayitliTema || "acik");

    temaButonu.addEventListener("click", function () {
        const mevcutCss = temaStili.getAttribute("href");
        temaUygula(mevcutCss.includes("beyaz.css") ? "koyu" : "acik");
    });
});