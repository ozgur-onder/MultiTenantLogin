(function () {
    function bildirimGoster(mesaj, tur = "basari") {
        const kutu = document.createElement("div");
        kutu.className = `bildirim bildirim-${tur} goster`;
        kutu.textContent = mesaj;
        document.body.appendChild(kutu);
        
        setTimeout(() => {
            kutu.classList.remove("goster");
            setTimeout(() => kutu.remove(), 300);
        }, 3000);
    }

    let globalFirmaVerisi = []; 

    function yonetimSekmesiAc() {
        Sekme.ac("yonetim", "Yönetim", (icerikAlani) => {
            const sablon = document.getElementById("sablon-yonetim");
            if (!sablon) return;
            
            icerikAlani.innerHTML = "";
            icerikAlani.appendChild(sablon.content.cloneNode(true));

            const firmaKarti = icerikAlani.querySelector("#kart-firma");
            if (firmaKarti) firmaKarti.addEventListener("click", firmaListesiSekmesiAc);
        });
    }

    function excelDisaAktar() {
        if (globalFirmaVerisi.length === 0) {
            bildirimGoster("Dışa aktarılacak veri bulunamadı.", "hata");
            return;
        }

        const excelVerisi = globalFirmaVerisi.map(f => ({
            "Firma Kodu": f.firma_kodu,
            "Firma Adı": f.firma_adi,
            "Durum": f.durum ? "Aktif" : "Pasif"
        }));

        const calismaSayfasi = XLSX.utils.json_to_sheet(excelVerisi);
        const calismaKitabi = XLSX.utils.book_new();
        XLSX.utils.book_append_sheet(calismaKitabi, calismaSayfasi, "Firmalar");
        
        XLSX.writeFile(calismaKitabi, "Firma_Listesi.xlsx");
        bildirimGoster("Excel dosyası başarıyla indirildi.", "basari");
    }

    function firmaListesiSekmesiAc() {
        Sekme.ac("firma_listesi", "Firmalar", async (icerikAlani) => {
            const sablon = document.getElementById("sablon-firma-listesi");
            if (!sablon) return;

            icerikAlani.innerHTML = "";
            icerikAlani.appendChild(sablon.content.cloneNode(true));

            const tabloAlani = icerikAlani.querySelector("#firma-tablo-alani");
            const mesajAlani = icerikAlani.querySelector("#firma-mesaj");
            
            const excelButonu = icerikAlani.querySelector("#excel-aktar-btn");
            if (excelButonu) excelButonu.addEventListener("click", excelDisaAktar);

            const ekleButonu = icerikAlani.querySelector("#yeni-firma-btn");
            if (ekleButonu) {
                ekleButonu.addEventListener("click", async () => {
                    const firmaKodu = prompt("Kısa Firma Kodu Girin (Örn: VNT):");
                    if (!firmaKodu) return;
                    const firmaAdi = prompt("Tam Firma Adı Girin:");
                    if (!firmaAdi) return;

                    try {
                        const yanit = await fetch("/api/firma", {
                            method: "POST",
                            headers: { "Content-Type": "application/json" },
                            body: JSON.stringify({ firma_kodu: firmaKodu, firma_adi: firmaAdi })
                        });
                        
                        if (yanit.ok) {
                            bildirimGoster("Firma başarıyla eklendi.", "basari");
                            firmaListesiSekmesiAc(); 
                        } else {
                            bildirimGoster("Eklenemedi. Kod mevcut veya yetkiniz yok.", "hata");
                        }
                    } catch (hata) {
                        bildirimGoster("Sunucuya ulaşılamıyor.", "hata");
                    }
                });
            }

            try {
                const yanit = await fetch("/api/firma");
                
                if (yanit.ok) {
                    const firmalar = await yanit.json();
                    globalFirmaVerisi = firmalar; 
                    
                    if (firmalar.length === 0) {
                        if (mesajAlani) mesajAlani.textContent = "Sistemde henüz kayıtlı firma bulunmuyor.";
                        return;
                    }

                    tabloAlani.innerHTML = ""; 
                    const satirSablonu = document.getElementById("sablon-firma-satiri");

                    firmalar.forEach(firma => {
                        const satirKlon = satirSablonu.content.cloneNode(true);
                        const satirAnaDiv = satirKlon.querySelector(".firma-satiri");
                        satirAnaDiv.dataset.kodu = firma.firma_kodu;
                        
                        satirKlon.querySelector(".firma-adi").textContent = firma.firma_adi || "İsimsiz Firma";
                        satirKlon.querySelector(".firma-kodu").textContent = "Kod: " + (firma.firma_kodu || "Yok");

                        const isAktif = firma.durum !== false;
                        const durumYazi = satirKlon.querySelector(".durum-yazi");
                        const toggleBtn = satirKlon.querySelector(".toggle-btn");

                        durumYazi.textContent = isAktif ? "Aktif" : "Pasif";
                        durumYazi.classList.add(isAktif ? "durum-aktif-yazi" : "durum-pasif-yazi");
                        if (isAktif) toggleBtn.classList.add("aktif");

                        toggleBtn.addEventListener("click", async function() {
                            const suAnAktifMi = this.classList.contains("aktif");
                            const yeniDurum = !suAnAktifMi; 

                            this.classList.toggle("aktif");
                            durumYazi.textContent = yeniDurum ? "Aktif" : "Pasif";
                            durumYazi.classList.toggle("durum-aktif-yazi", yeniDurum);
                            durumYazi.classList.toggle("durum-pasif-yazi", !yeniDurum);

                            try {
                                const y = await fetch(`/api/firma/${firma.firma_kodu}/durum`, {
                                    method: "PATCH",
                                    headers: { "Content-Type": "application/json" },
                                    body: JSON.stringify({ durum: yeniDurum })
                                });

                                if (y.ok) {
                                    bildirimGoster(`Firma durumu ${yeniDurum ? 'Aktif' : 'Pasif'} yapıldı.`, "basari");
                                    const guncellenenFirma = globalFirmaVerisi.find(f => f.firma_kodu === firma.firma_kodu);
                                    if (guncellenenFirma) guncellenenFirma.durum = yeniDurum;
                                } else {
                                    throw new Error("Güncelleme reddedildi.");
                                }
                            } catch(e) {
                                bildirimGoster("Durum güncellenemedi! İşlem geri alındı.", "hata");
                                this.classList.toggle("aktif");
                                durumYazi.textContent = suAnAktifMi ? "Aktif" : "Pasif";
                                durumYazi.classList.toggle("durum-aktif-yazi", suAnAktifMi);
                                durumYazi.classList.toggle("durum-pasif-yazi", !suAnAktifMi);
                            }
                        });

                        tabloAlani.appendChild(satirKlon);
                    });
                } else {
                    if (mesajAlani) mesajAlani.textContent = "Firmalar alınamadı. Yetkiniz olmayabilir.";
                }
            } catch (hata) {
                if (mesajAlani) mesajAlani.textContent = "Sunucu bağlantı hatası.";
            }
        });
    }

    document.addEventListener("DOMContentLoaded", () => {
        const yonetimButonu = document.querySelector('[data-sayfa="yonetim"]');
        if (yonetimButonu) {
            yonetimButonu.addEventListener("click", yonetimSekmesiAc);
        }
    });
})();