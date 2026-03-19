document.addEventListener('DOMContentLoaded', () => {
    // Universal Reveal Animation
    const revealElements = document.querySelectorAll('.reveal-up, .fade-up, section, .glass-panel:not(.dropdown-content)');
    const revealObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('active', 'visible');
                // Legacy support for direct style manipulation if needed
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, { threshold: 0.1, rootMargin: '0px 0px -50px 0px' });

    revealElements.forEach(el => {
        if (!el.classList.contains('active') && !el.classList.contains('visible')) {
            el.style.opacity = '0';
            el.style.transform = 'translateY(20px)';
        }
        revealObserver.observe(el);
    });

    // Auto-dismiss Django messages after 5 seconds
    const messages = document.querySelectorAll('.alert');
    if (messages.length > 0) {
        setTimeout(() => {
            messages.forEach(msg => {
                msg.style.opacity = '0';
                msg.style.transform = 'translateY(-20px)';
                setTimeout(() => msg.remove(), 300);
            });
        }, 5000);
    }
    // Animated Counter Logic
    const counters = document.querySelectorAll('.stat-number');
    const animateCounters = () => {
        counters.forEach(counter => {
            const target = parseInt(counter.innerText.replace(/\D/g, ''));
            const suffix = counter.innerText.match(/\D/g)?.join('') || '';
            let count = 0;
            const speed = target / 50; // Adjust for speed
            
            const updateCount = () => {
                if (count < target) {
                    count += Math.ceil(speed);
                    counter.innerText = (count > target ? target : count) + suffix;
                    setTimeout(updateCount, 20);
                } else {
                    counter.innerText = target + suffix;
                }
            };
            updateCount();
        });
    };

    const statsObserver = new IntersectionObserver((entries) => {
        if (entries[0].isIntersecting) {
            animateCounters();
            statsObserver.disconnect(); // Run once
        }
    }, { threshold: 0.5 });

    if (counters.length > 0) {
        statsObserver.observe(counters[0].parentElement);
    }
});
