// === Логіка Сайдбару ===
const sidebar = document.getElementById('sidebar');
const toggle  = document.getElementById('sidebarToggle');
const overlay = document.getElementById('sidebarOverlay');

function openSidebar() {
    sidebar.classList.add('open');
    overlay.style.display = 'block';
    document.body.style.overflow = 'hidden';
}

function closeSidebar() {
    sidebar.classList.remove('open');
    overlay.style.display = 'none';
    document.body.style.overflow = 'auto';
}

if (toggle) {
    toggle.addEventListener('click', () => {
        sidebar.classList.contains('open') ? closeSidebar() : openSidebar();
    });
}
if (overlay) {
    overlay.addEventListener('click', closeSidebar);
}

async function loadData() {
    const loader = document.getElementById('loader');
    const container = document.getElementById('items-grid');
    const errorContainer = document.getElementById('error-container');

    if (loader) loader.style.display = 'flex';
    if (errorContainer) errorContainer.innerHTML = '';
    await new Promise(resolve => setTimeout(resolve, 800));

    try {
        const response = await fetch('/static/core/data.json');
        if (!response.ok) {
            throw new Error(`HTTP Error: ${response.status}`);
        }
        const dataArray = await response.json();
        renderCards(dataArray, container);
        initFilters();

    } catch (error) {
        console.error("Fetch Error:", error);
        if (errorContainer) {
            errorContainer.innerHTML = `
                <div class="fetch-error">
                    <i data-lucide="wifi-off" style="width:32px;height:32px;margin-bottom:10px;"></i>
                    <h3>Помилка завантаження</h3>
                    <p>Вибачте, дані тимчасово недоступні. Спробуйте оновити сторінку.</p>
                </div>
            `;
            if (window.lucide) lucide.createIcons();
        }
    } finally {
        if (loader) loader.style.display = 'none';
    }
}

function renderCards(dataArray, container) {
    if (!container) return;

    container.innerHTML = '';

    dataArray.forEach(item => {
        const stockStatus = item.inStock
            ? '<span class="text-accent" style="font-size:11px;">В наявності</span>'
            : '<span class="text-muted" style="font-size:11px;">Немає в наявності</span>';

        const cardHTML = `
            <a href="/book/${item.id}/" class="book-card" data-category="${item.genre}">
                <div class="book-card__spine-wrap">
                    <div class="book-card__cover">
                        <img src="${item.image}" alt="${item.title}" loading="lazy"
                             onerror="this.parentElement.innerHTML='<div class=\\'book-card__no-cover\\'>${item.title}</div>'">
                    </div>
                </div>
                <div class="book-card__meta">
                    <div class="book-card__title">${item.title}</div>
                    <div class="book-card__author">${item.author}</div>
                    ${stockStatus}
                </div>
            </a>
        `;
        container.insertAdjacentHTML('beforeend', cardHTML);
    });
}

function initFilters() {
    const filterButtons = document.querySelectorAll('.filter-btn');
    const bookCards = document.querySelectorAll('.book-card');

    filterButtons.forEach(button => {
        button.addEventListener('click', () => {
            filterButtons.forEach(btn => {
                btn.classList.remove('btn-primary');
                btn.classList.add('btn-ghost');
            });

            button.classList.remove('btn-ghost');
            button.classList.add('btn-primary');

            const filterValue = button.getAttribute('data-filter');

            bookCards.forEach(card => {
                const cardCategory = card.getAttribute('data-category');
                if (filterValue === 'all' || filterValue === cardCategory) {
                    card.classList.remove('hidden');
                } else {
                    card.classList.add('hidden');
                }
            });
        });
    });
}

// === Ініціалізація всіх скриптів при завантаженні DOM ===
document.addEventListener('DOMContentLoaded', () => {
    // Запускаємо логіку завантаження даних (Практична 4)
    if (document.getElementById('items-grid')) {
        loadData();
    }

    // Анімація та блокування кнопок відправки форм
    const submitButtons = document.querySelectorAll('button[type="submit"]');
    submitButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            const form = this.closest('form');
            if (form && form.checkValidity()) {
                setTimeout(() => {
                    this.disabled = true;
                    this.innerHTML = 'Processing...';
                    this.style.transform = 'scale(0.95)';
                    this.style.opacity = '0.7';
                }, 10);
            }
        });
    });

    // Динамічні лайки без перезавантаження
    const likeButtons = document.querySelectorAll('.like-btn');
    likeButtons.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            this.classList.toggle('liked');

            const icon = this.querySelector('svg');
            if (icon) {
                if (this.classList.contains('liked')) {
                    icon.style.fill = 'currentColor';
                    icon.style.transform = 'scale(1.1)';
                } else {
                    icon.style.fill = 'none';
                    icon.style.transform = 'scale(1)';
                }
            }
        });
    });

    // Закриття сайдбару при кліку на лінк
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', () => {
            if (sidebar.classList.contains('open')) {
                closeSidebar();
            }
        });
    });
});