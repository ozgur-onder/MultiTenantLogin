(function () {
    const DEPOLAMA_ANAHTARI = "secilen-tema";
    
    const SIYAH_YOL  = "/temalar/sifremi_unuttum/siyah.css";
    const BEYAZ_YOL  = "/temalar/sifremi_unuttum/beyaz.css";

    const AY_IKONU = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75">
        <path stroke-linecap="round" stroke-linejoin="round"
            d="M21.752 15.002A9.72 9.72 0 0118 15.75c-5.385 0-9.75-4.365-9.75-9.75 0-1.33.266-2.597.748-3.752A9.753 9.753 0 003 11.25C3 16.635 7.365 21 12.75 21a9.753 9.753 0 009.002-5.998z"/>
    </svg>`;

    const GUNES_IKONU = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75">
        <path stroke-linecap="round" stroke-linejoin="round"
            d="M12 3v2.25m6.364.386l-1.591 1.591M21 12h-2.25m-.386 6.364l-1.591-1.591M12 18.75V21m-4.773-4.227l-1.591 1.591M5.25 12H3m4.227-4.773L5.636 5.636M15.75 12a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0z"/>
    </svg>`;

    function temaUygula(tema) {
        const link = document.getElementById("tema-stili");
        const btn  = document.getElementById("tema-btn");
        if (!link || !btn) return;

        if (tema === "koyu" || tema === "siyah") {
            link.setAttribute("href", SIYAH_YOL);
            btn.innerHTML = GUNES_IKONU;
            localStorage.setItem(DEPOLAMA_ANAHTARI, "koyu");
        } else {
            link.setAttribute("href", BEYAZ_YOL);
            btn.innerHTML = AY_IKONU;
            localStorage.setItem(DEPOLAMA_ANAHTARI, "acik");
        }
    }

    function basla() {
        const kayitli = localStorage.getItem(DEPOLAMA_ANAHTARI) || "koyu";
        temaUygula(kayitli);

        document.getElementById("tema-btn")?.addEventListener("click", () => {
            const mevcutKoyuMu = document.getElementById("tema-stili")?.getAttribute("href")?.includes("siyah");
            temaUygula(mevcutKoyuMu ? "acik" : "koyu");
        });
    }

    document.addEventListener("DOMContentLoaded", basla);
})();