// DocMind AI - Custom Javascript & Micro-Interactions
document.addEventListener('DOMContentLoaded', () => {
    console.log("DocMind AI UI Engine initialized successfully.");
    
    // Auto-dismiss Toast notifications after 4 seconds
    const toastElList = document.querySelectorAll('.toast');
    [...toastElList].forEach(toastEl => {
        setTimeout(() => {
            const bsToast = bootstrap.Toast.getInstance(toastEl) || new bootstrap.Toast(toastEl);
            bsToast.hide();
        }, 4000);
    });

    // Smooth Scroll for Navigation Anchor Links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const targetId = this.getAttribute('href');
            if (targetId && targetId !== '#') {
                const targetElement = document.querySelector(targetId);
                if (targetElement) {
                    e.preventDefault();
                    targetElement.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
        });
    });

    // Landing Page FAQ Accordion Toggles
    const faqItems = document.querySelectorAll('.faq-accordion-header');
    faqItems.forEach(header => {
        header.addEventListener('click', () => {
            const parent = header.parentElement;
            parent.classList.toggle('active');
        });
    });
});
