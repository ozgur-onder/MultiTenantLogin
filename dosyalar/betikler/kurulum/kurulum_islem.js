document.addEventListener("DOMContentLoaded", function () {
    const submitBtn = document.getElementById('submitBtn');

    if (submitBtn) {
        submitBtn.addEventListener('click', async function () {
            const ad = document.getElementById('ad').value.trim();
            const soyad = document.getElementById('soyad').value.trim();
            const sicil_no = document.getElementById('sicil-no').value.trim();
            const email = document.getElementById('email').value.trim();
            const passwordInput = document.getElementById('password');
            const p1 = passwordInput ? passwordInput.value : '';
            
            const smtp_sunucu = document.getElementById('smtp-sunucu').value.trim();
            const smtp_port = document.getElementById('smtp-port').value.trim();
            const smtp_email = document.getElementById('smtp-email').value.trim();
            const smtp_sifre = document.getElementById('smtp-sifre').value;
            const smtp_gonderici = document.getElementById('smtp-gonderici').value.trim();

            if (!smtp_sunucu || !smtp_port || !smtp_email || !smtp_sifre || !smtp_gonderici) {
                window.showNotification("Lütfen tüm mail ayarlarını eksiksiz doldurun.", "error");
                return;
            }

            if (!window.isValidEmail(smtp_email)) {
                window.showNotification("Lütfen geçerli bir gönderici e-posta adresi girin.", "error");
                return;
            }

            const originalText = submitBtn.innerText;
            submitBtn.innerText = "Kuruluyor...";
            submitBtn.disabled = true;

            const formData = new FormData();
            formData.append("ad", ad); 
            formData.append("soyad", soyad); 
            formData.append("sicil_no", sicil_no); 
            formData.append("email", email); 
            formData.append("sifre", p1);
            
            formData.append("smtp_sunucu", smtp_sunucu);
            formData.append("smtp_port", smtp_port);
            formData.append("smtp_email", smtp_email);
            formData.append("smtp_sifre", smtp_sifre);
            formData.append("smtp_gonderici", smtp_gonderici);

            try {
                const response = await fetch('/kurulum-tamamla', {
                    method: 'POST',
                    body: formData
                });

                if (response.ok) {
                    const data = await response.json();
                    window.showNotification(data.mesaj, "success"); 
                    setTimeout(() => {
                        window.location.href = "/";
                    }, 1500);
                } else {
                    const errorData = await response.json();
                    window.showNotification(errorData.detail || "Kurulum sırasında sunucu hatası oluştu.", "error");
                    submitBtn.innerText = originalText;
                    submitBtn.disabled = false;
                }
            } catch (error) {
                console.error("Hata:", error);
                window.showNotification("Sunucuya ulaşılamıyor. Lütfen bağlantınızı kontrol edin.", "error");
                submitBtn.innerText = originalText;
                submitBtn.disabled = false;
            }
        });
    }
});