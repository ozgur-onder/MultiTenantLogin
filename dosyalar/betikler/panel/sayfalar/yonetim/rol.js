const RolYonetimi = (function () {
    let globalRolVerisi = [];

    function excelIndir(veriDizisi, dosyaAdi, sayfaAdi) {
        if (!veriDizisi || veriDizisi.length === 0) {
            Bildirim.goster("uyari", "Dışa aktarılacak veri bulunamadı.");
            return;
        }
        try {
            const calismaSayfasi = XLSX.utils.json_to_sheet(veriDizisi);
            const calismaKitabi = XLSX.utils.book_new();
            XLSX.utils.book_append_sheet(calismaKitabi, calismaSayfasi, sayfaAdi);
            XLSX.writeFile(calismaKitabi, dosyaAdi);
        } catch (hata) {
            Bildirim.goster("hata", "Excel dosyası oluşturulamadı.");
        }
    }

    async function yanitiIsle(yanit) {
        try {
            const veri = await yanit.json();
            return { basarili: yanit.ok, mesaj: veri.detail || veri.mesaj || "İşlem sonucu belirsiz." };
        } catch (e) {
            return { basarili: yanit.ok, mesaj: yanit.ok ? "İşlem başarılı." : "Sunucu geçersiz bir yanıt döndürdü." };
        }
    }

    function yeniRolModalAc(basariCallback) {
        const sablon = document.getElementById("sablon-rol-modal");
        if (!sablon) return;

        const modalKlon = sablon.content.cloneNode(true);
        const arkaplan = modalKlon.querySelector("#rol-modal-arkaplan");
        
        document.body.appendChild(arkaplan);

        const inputKod = arkaplan.querySelector("#modal-rol-kodu");
        const inputAdi = arkaplan.querySelector("#modal-rol-adi");
        const btnKaydet = arkaplan.querySelector("#modal-rol-kaydet-btn");
        const btnIptal = arkaplan.querySelector("#modal-rol-iptal-btn");

        if (inputKod) inputKod.focus();

        const kapat = () => arkaplan.remove();

        if (btnIptal) btnIptal.addEventListener("click", kapat);
        arkaplan.addEventListener("click", (e) => {
            if (e.target === arkaplan) kapat();
        });

        if (btnKaydet) {
            btnKaydet.addEventListener("click", async () => {
                const rolKodu = parseInt(inputKod.value.trim());
                const rolAdi = inputAdi.value.trim();

                if (!rolKodu || !rolAdi) {
                    Bildirim.goster("uyari", "Lütfen tüm alanları doldurun.");
                    return;
                }

                try {
                    const yanit = await fetch("/api/rol", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ rol_kodu: rolKodu, rol_adi: rolAdi })
                    });

                    const sonuc = await yanitiIsle(yanit);

                    if (sonuc.basarili) {
                        kapat();
                        Bildirim.goster("basari", sonuc.mesaj);
                        if (basariCallback) basariCallback();
                    } else {
                        Bildirim.goster("hata", sonuc.mesaj);
                    }
                } catch (e) {
                    Bildirim.goster("hata", "Sunucuya bağlanılamadı.");
                }
            });
        }
    }

    async function tabloyuGuncelle() {
        // ÇÖZÜM: Görünmez şablonu (template) değil, sadece aktif sayfadaki alanı hedefliyoruz
        const canliAlan = document.getElementById("sayfa-icerik");
        if (!canliAlan) return;
        
        const tabloGovdesi = canliAlan.querySelector("#rol-tablo-govdesi");
        if (!tabloGovdesi) return;

        try {
            const cacheKirici = new Date().getTime();
            const yanit = await fetch(`/api/rol?_t=${cacheKirici}`, {
                headers: { 'Cache-Control': 'no-cache', 'Pragma': 'no-cache' }
            });

            if (yanit.ok) {
                const roller = await yanit.json();
                globalRolVerisi = roller;

                if (roller.length === 0) {
                    tabloGovdesi.innerHTML = '<tr><td colspan="5" class="yukleniyor">Kayıtlı rol bulunmuyor.</td></tr>';
                    return;
                }

                tabloGovdesi.innerHTML = "";
                const satirSablonu = document.getElementById("sablon-rol-satiri");

                roller.forEach(rol => {
                    const satirKlon = satirSablonu.content.cloneNode(true);

                    satirKlon.querySelector(".rol-kodu").textContent = rol["Rol Kodu"];
                    satirKlon.querySelector(".rol-adi").textContent = rol["Rol Adı"];

                    const detayMetni = `${rol["İşlem Yapan Sicil"]} — ${rol["Son İşlem Zamanı"]}`;
                    satirKlon.querySelector(".rol-detay").textContent = detayMetni;

                    // let: tıklama sonrası state güncellenebilsin
                    let aktifMi = rol["Durum"] === "Aktif";
                    const badge = satirKlon.querySelector(".durum-badge");
                    const aksiyonBtn = satirKlon.querySelector(".aksiyon-btn");

                    // Badge + buton DOM güncellemesini tek yerden yönet
                    function satirDurumGuncelle(durum) {
                        badge.textContent = durum ? "Aktif" : "Pasif";
                        badge.classList.remove("badge-aktif", "badge-pasif");
                        badge.classList.add(durum ? "badge-aktif" : "badge-pasif");
                        aksiyonBtn.textContent = durum ? "Pasife Al" : "Aktifleştir";
                        aksiyonBtn.classList.remove("btn-tehlike", "btn-basari");
                        aksiyonBtn.classList.add(durum ? "btn-tehlike" : "btn-basari");
                    }

                    satirDurumGuncelle(aktifMi);

                    aksiyonBtn.addEventListener("click", async function () {
                        const yeniDurum = !aktifMi;

                        // 1) Anlık (optimistik) güncelleme — API'yi beklemeden ekrana yansıt
                        satirDurumGuncelle(yeniDurum);
                        aksiyonBtn.disabled = true;

                        try {
                            const y = await fetch(`/api/rol/${rol["Rol Kodu"]}/durum`, {
                                method: "PATCH",
                                headers: { "Content-Type": "application/json" },
                                body: JSON.stringify({ durum: yeniDurum })
                            });

                            const sonuc = await yanitiIsle(y);

                            if (sonuc.basarili) {
                                // 2) State'i kalıcı olarak güncelle
                                aktifMi = yeniDurum;
                                // Excel export'unun güncel veriyle çalışması için globalRolVerisi'ni de güncelle
                                const idx = globalRolVerisi.findIndex(r => r["Rol Kodu"] === rol["Rol Kodu"]);
                                if (idx !== -1) globalRolVerisi[idx]["Durum"] = yeniDurum ? "Aktif" : "Pasif";
                                Bildirim.goster("basari", sonuc.mesaj);
                            } else {
                                // 3) Hata: eski hale geri al
                                satirDurumGuncelle(aktifMi);
                                Bildirim.goster("hata", sonuc.mesaj);
                            }
                        } catch (e) {
                            // 3) Ağ hatası: eski hale geri al
                            satirDurumGuncelle(aktifMi);
                            Bildirim.goster("hata", "Sunucuya bağlanılamadı.");
                        } finally {
                            aksiyonBtn.disabled = false;
                        }
                    });

                    tabloGovdesi.appendChild(satirKlon);
                });
            } else {
                const sonuc = await yanitiIsle(yanit);
                tabloGovdesi.innerHTML = `<tr><td colspan="5" class="yukleniyor">${sonuc.mesaj}</td></tr>`;
            }
        } catch (hata) {
            tabloGovdesi.innerHTML = '<tr><td colspan="5" class="yukleniyor">Veri çekilemedi. Bağlantı hatası.</td></tr>';
        }
    }

    function baslat() {
        Sekme.ac("rol_listesi", "Rol Yönetimi", async (icerikAlani) => {
            const sablon = document.getElementById("sablon-rol-listesi");
            if (!sablon) return;

            icerikAlani.innerHTML = "";
            icerikAlani.appendChild(sablon.content.cloneNode(true));

            const excelBtn = icerikAlani.querySelector("#rol-excel-aktar-btn");
            if (excelBtn) {
                excelBtn.addEventListener("click", () => excelIndir(globalRolVerisi, "Rol_Listesi.xlsx", "Roller"));
            }

            const logBtn = icerikAlani.querySelector("#rol-log-aktar-btn");
            if (logBtn) {
                logBtn.addEventListener("click", async () => {
                    try {
                        const cacheKirici = new Date().getTime();
                        const yanit = await fetch(`/api/rol/loglar?_t=${cacheKirici}`, {
                            headers: { 'Cache-Control': 'no-cache', 'Pragma': 'no-cache' }
                        });
                        if (yanit.ok) {
                            excelIndir(await yanit.json(), "Rol_Guncelleme_Loglari.xlsx", "Loglar");
                        } else {
                            const sonuc = await yanitiIsle(yanit);
                            Bildirim.goster("hata", sonuc.mesaj);
                        }
                    } catch (hata) {
                        Bildirim.goster("hata", "Sunucuya bağlanılamadı.");
                    }
                });
            }

            const ekleBtn = icerikAlani.querySelector("#yeni-rol-btn");
            if (ekleBtn) {
                ekleBtn.addEventListener("click", () => {
                    yeniRolModalAc(() => tabloyuGuncelle());
                });
            }

            // Sekme açıldığı an tabloyu doldur
            tabloyuGuncelle();
        });
    }

    return { baslat };
})();