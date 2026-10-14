document.addEventListener('DOMContentLoaded', () => {
    // Menú móvil responsive
    const hamburger = document.querySelector('.hamburger');
    const navLinks = document.querySelector('.nav-links');

    if (hamburger && navLinks) {
        hamburger.addEventListener('click', () => {
            navLinks.classList.toggle('open');
        });
    }

    // Bloquear clic derecho en contenido público
    document.addEventListener('contextmenu', (e) => {
        if (!window.location.pathname.startsWith('/admin')) {
            e.preventDefault();
        }
    });

    // Bloquear atajos comunes de inspección rápida
    document.addEventListener('keydown', (e) => {
        if (!window.location.pathname.startsWith('/admin')) {
            if (e.key === 'F12' || (e.ctrlKey && e.shiftKey && (e.key === 'I' || e.key === 'J')) || (e.ctrlKey && e.key === 'U')) {
                e.preventDefault();
            }
        }
    });
});