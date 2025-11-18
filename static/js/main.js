// Мобильное меню
document.addEventListener('DOMContentLoaded', function() {
    const mobileMenuToggle = document.getElementById('mobileMenuToggle');
    const navbarCollapse = document.getElementById('navbarCollapse');

    if (mobileMenuToggle) {
        mobileMenuToggle.addEventListener('click', function() {
            this.classList.toggle('active');
            navbarCollapse.classList.toggle('active');
            document.body.classList.toggle('menu-open');
        });

        // Закрытие меню при клике на ссылку
        const menuLinks = navbarCollapse.querySelectorAll('a');
        menuLinks.forEach(link => {
            link.addEventListener('click', function() {
                mobileMenuToggle.classList.remove('active');
                navbarCollapse.classList.remove('active');
                document.body.classList.remove('menu-open');
            });
        });

        // Закрытие меню при клике вне его
        document.addEventListener('click', function(event) {
            if (!event.target.closest('.navbar')) {
                mobileMenuToggle.classList.remove('active');
                navbarCollapse.classList.remove('active');
                document.body.classList.remove('menu-open');
            }
        });
    }
});

// Автозакрытие алертов через 5 секунд
document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => {
                alert.style.display = 'none';
            }, 300);
        }, 5000);
    });
});

// Анимация для slideOut
const style = document.createElement('style');
style.textContent = `
    @keyframes slideOut {
        from {
            opacity: 1;
            transform: translateY(0);
        }
        to {
            opacity: 0;
            transform: translateY(-10px);
        }
    }
`;
document.head.appendChild(style);
