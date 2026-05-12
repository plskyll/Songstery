document.querySelectorAll('button[type="submit"]').forEach(btn => {
    btn.addEventListener('click', function () {
        const form = this.closest('form');
        if (form && form.checkValidity()) {
            setTimeout(() => {
                this.disabled = true;
                this.textContent = 'Processing…';
            }, 10);
        }
    });
});