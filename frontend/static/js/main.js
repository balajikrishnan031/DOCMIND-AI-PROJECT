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

    // 1. Intersection Observer Scroll Reveal Animation Engine
    const scrollObserverOptions = {
        threshold: 0.15,
        rootMargin: "0px 0px -50px 0px"
    };

    const scrollObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('in-view');
                observer.unobserve(entry.target);
            }
        });
    }, scrollObserverOptions);

    document.querySelectorAll('.animate-fade-in-up, .glass-card-base, .glass-panel').forEach(el => {
        scrollObserver.observe(el);
    });

    // 2. Interactive Cursor Particle Glow Follower
    const cursorGlow = document.createElement('div');
    cursorGlow.className = 'cursor-particle-glow';
    cursorGlow.style.cssText = `
        position: fixed;
        width: 300px;
        height: 300px;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(56, 189, 248, 0.15) 0%, rgba(192, 132, 252, 0.08) 50%, transparent 70%);
        pointer-events: none;
        z-index: 9999;
        transform: translate(-50%, -50%);
        transition: transform 0.15s ease-out, opacity 0.3s ease;
        opacity: 0;
    `;
    document.body.appendChild(cursorGlow);

    document.addEventListener('mousemove', (e) => {
        cursorGlow.style.left = `${e.clientX}px`;
        cursorGlow.style.top = `${e.clientY}px`;
        cursorGlow.style.opacity = '1';
    });

    document.addEventListener('mouseleave', () => {
        cursorGlow.style.opacity = '0';
    });

    // 3. 3D Card Tilt Effect on Hover
    document.querySelectorAll('.glass-card-base, .preview-mockup-card').forEach(card => {
        card.addEventListener('mousemove', (e) => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            const rotateX = ((y - centerY) / centerY) * -6;
            const rotateY = ((x - centerX) / centerX) * 6;

            card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-6px)`;
        });

        card.addEventListener('mouseleave', () => {
            card.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg) translateY(0px)';
        });
    });
});
