/**
 * sekme.js — Tab (sekme) yönetim modülü
 * API: Sekme.ac(id, baslik), Sekme.aktiflestir(id), Sekme.kapat(id)
 */
const Sekme = (function () {
    const sekmeler   = new Map();   // id → { baslik, icerik }
    let   aktifSekme = null;

    function _barElemaniniAl() {
        return document.getElementById("sekme-bar");
    }

    function _icerikAlaniAl() {
        return document.getElementById("sayfa-icerik");
    }

    function _sekmeElemaniOlustur(id, baslik) {
        const el = document.createElement("div");
        el.className  = "sekme";
        el.dataset.id = id;
        el.innerHTML  = `
            <span class="sekme-yazi">${baslik}</span>
            ${id !== "anasayfa" ? '<span class="sekme-kapat" data-kapat="true">×</span>' : ""}
        `;

        el.addEventListener("click", (e) => {
            if (e.target.dataset.kapat) {
                kapat(id);
            } else {
                aktiflestir(id);
            }
        });

        return el;
    }

    function ac(id, baslik, icerikFn) {
        if (sekmeler.has(id)) {
            aktiflestir(id);
            return;
        }

        sekmeler.set(id, { baslik, icerikFn });
        const bar = _barElemaniniAl();
        if (bar) bar.appendChild(_sekmeElemaniOlustur(id, baslik));

        aktiflestir(id);
    }

    function aktiflestir(id) {
        if (!sekmeler.has(id)) return;

        aktifSekme = id;

        // Sekme elementlerini güncelle
        document.querySelectorAll(".sekme").forEach(el => {
            el.classList.toggle("aktif", el.dataset.id === id);
        });

        // İçeriği render et
        const { icerikFn } = sekmeler.get(id);
        const icerikAlani  = _icerikAlaniAl();
        if (icerikAlani && typeof icerikFn === "function") {
            icerikAlani.innerHTML = "";
            icerikFn(icerikAlani);
        }
    }

    function kapat(id) {
        if (id === "anasayfa" || !sekmeler.has(id)) return;

        sekmeler.delete(id);

        // Sekme elementini kaldır
        const el = document.querySelector(`.sekme[data-id="${id}"]`);
        if (el) el.remove();

        // Kapanıyorsa bir öncekine dön
        if (aktifSekme === id) {
            const sonrakiId = sekmeler.size > 0
                ? [...sekmeler.keys()].at(-1)
                : null;
            if (sonrakiId) aktiflestir(sonrakiId);
        }
    }

    function aktifId() { return aktifSekme; }

    return { ac, aktiflestir, kapat, aktifId };
})();