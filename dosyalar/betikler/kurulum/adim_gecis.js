document.addEventListener("DOMContentLoaded", function () {
    const ileriBtn = document.getElementById('ileriBtn');
    const geriBtn = document.getElementById('geriBtn');
    const step1 = document.getElementById('step-1');
    const step2 = document.getElementById('step-2');
    const passwordInput = document.getElementById('password');
    const confirmInput = document.getElementById('password-confirm');

    if(ileriBtn) {
        ileriBtn.addEventListener('click', function() {
            const ad = document.getElementById('ad').value.trim();
            const soyad = document.getElementById('soyad').value.trim();
            const sicil_no = document.getElementById('sicil-no').value.trim();
            const email = document.getElementById('email').value.trim();
            const p1 = passwordInput ? passwordInput.value : '';
            const p2 = confirmInput ? confirmInput.value : '';

            if (!ad || !soyad || !sicil_no || !email || !p1 || !p2) {
                window.showNotification("Lütfen tüm yönetici bilgilerini eksiksiz doldurun.", "error");
                return;
            }

            if (!window.isValidEmail(email)) {
                window.showNotification("Lütfen geçerli bir e-posta adresi girin.", "error");
                return;
            }

            if (!window.isPasswordValid) {
                window.showNotification("Lütfen tüm güvenlik kurallarını karşılayan bir parola belirleyin.", "error");
                return;
            }
            if (p1 !== p2) {
                window.showNotification("Girdiğiniz parolalar eşleşmiyor.", "error");
                return;
            }

            if(step1 && step2) {
                step1.classList.remove('active');
                step2.classList.add('active');
            }
        });
    }

    if(geriBtn) {
        geriBtn.addEventListener('click', function() {
            if(step1 && step2) {
                step2.classList.remove('active');
                step1.classList.add('active');
            }
        });
    }
});