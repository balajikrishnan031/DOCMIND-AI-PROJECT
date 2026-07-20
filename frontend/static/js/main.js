// DocMind AI - Custom Javascript
document.addEventListener('DOMContentLoaded', () => {
    console.log("DocMind AI initialized successfully.");
    
    // Auto-dismiss Toast notifications after 4 seconds
    const toastElList = document.querySelectorAll('.toast');
    const toastList = [...toastElList].map(toastEl => {
        setTimeout(() => {
            const bsToast = bootstrap.Toast.getInstance(toastEl) || new bootstrap.Toast(toastEl);
            bsToast.hide();
        }, 4000);
    });
});
