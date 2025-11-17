/**
 * Основной JavaScript для системы управления ДМОС
 */

// Автоматическое закрытие алертов через 5 секунд
document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            alert.style.opacity = '0';
            setTimeout(function() {
                alert.style.display = 'none';
            }, 300);
        }, 5000);
    });
});

// Подтверждение при удалении
function confirmDelete(message) {
    return confirm(message || 'Вы уверены, что хотите удалить?');
}

// Валидация форм
document.addEventListener('DOMContentLoaded', function() {
    const forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            const requiredFields = form.querySelectorAll('[required]');
            let isValid = true;

            requiredFields.forEach(function(field) {
                if (!field.value.trim()) {
                    isValid = false;
                    field.style.borderColor = 'var(--danger-color)';
                } else {
                    field.style.borderColor = 'var(--border-color)';
                }
            });

            if (!isValid) {
                e.preventDefault();
                alert('Пожалуйста, заполните все обязательные поля');
            }
        });
    });
});

// Превью изображений перед загрузкой
function previewImage(input, previewId) {
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        reader.onload = function(e) {
            document.getElementById(previewId).src = e.target.result;
        };
        reader.readAsDataURL(input.files[0]);
    }
}

// Фильтрация списков
function filterList(inputId, listClass) {
    const input = document.getElementById(inputId);
    const filter = input.value.toLowerCase();
    const items = document.querySelectorAll(`.${listClass}`);

    items.forEach(function(item) {
        const text = item.textContent.toLowerCase();
        if (text.indexOf(filter) > -1) {
            item.style.display = '';
        } else {
            item.style.display = 'none';
        }
    });
}

// Переключение видимости пароля
function togglePassword(buttonId, inputId) {
    const button = document.getElementById(buttonId);
    const input = document.getElementById(inputId);

    button.addEventListener('click', function() {
        if (input.type === 'password') {
            input.type = 'text';
            button.textContent = 'Скрыть';
        } else {
            input.type = 'password';
            button.textContent = 'Показать';
        }
    });
}

// Копирование текста в буфер обмена
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(function() {
        showNotification('Скопировано в буфер обмена', 'success');
    }).catch(function(err) {
        console.error('Ошибка копирования:', err);
    });
}

// Показ уведомлений
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type}`;
    notification.textContent = message;
    notification.style.position = 'fixed';
    notification.style.top = '20px';
    notification.style.right = '20px';
    notification.style.zIndex = '1000';

    document.body.appendChild(notification);

    setTimeout(function() {
        notification.style.opacity = '0';
        setTimeout(function() {
            notification.remove();
        }, 300);
    }, 3000);
}

// Подсчет символов в textarea
function setupCharCounter(textareaId, maxLength) {
    const textarea = document.getElementById(textareaId);
    if (!textarea) return;

    const counter = document.createElement('div');
    counter.className = 'char-counter';
    counter.style.textAlign = 'right';
    counter.style.fontSize = '0.875rem';
    counter.style.color = 'var(--text-secondary)';
    textarea.parentNode.appendChild(counter);

    function updateCounter() {
        const remaining = maxLength - textarea.value.length;
        counter.textContent = `${remaining} символов осталось`;
        if (remaining < 0) {
            counter.style.color = 'var(--danger-color)';
        } else {
            counter.style.color = 'var(--text-secondary)';
        }
    }

    textarea.addEventListener('input', updateCounter);
    updateCounter();
}

// Форматирование даты
function formatDate(date, format = 'DD.MM.YYYY') {
    const d = new Date(date);
    const day = String(d.getDate()).padStart(2, '0');
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const year = d.getFullYear();
    const hours = String(d.getHours()).padStart(2, '0');
    const minutes = String(d.getMinutes()).padStart(2, '0');

    return format
        .replace('DD', day)
        .replace('MM', month)
        .replace('YYYY', year)
        .replace('HH', hours)
        .replace('mm', minutes);
}

// Проверка валидности email
function isValidEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

// Проверка валидности телефона (российский формат)
function isValidPhone(phone) {
    const re = /^(\+7|8)?[\s-]?\(?[0-9]{3}\)?[\s-]?[0-9]{3}[\s-]?[0-9]{2}[\s-]?[0-9]{2}$/;
    return re.test(phone);
}

// Debounce функция для оптимизации поиска
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Экспорт функций для использования в других скриптах
window.CouncilApp = {
    confirmDelete,
    previewImage,
    filterList,
    copyToClipboard,
    showNotification,
    setupCharCounter,
    formatDate,
    isValidEmail,
    isValidPhone,
    debounce
};
