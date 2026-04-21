const sidebar = document.getElementById('sidebar');
const toggle  = document.getElementById('sidebarToggle');
const overlay = document.getElementById('sidebarOverlay');

function openSidebar() {
  sidebar.classList.add('open');
  overlay.style.display = 'block';
}
function closeSidebar() {
  sidebar.classList.remove('open');
  overlay.style.display = 'none';
}

if (toggle) {
    toggle.addEventListener('click', () => {
        sidebar.classList.contains('open') ? closeSidebar() : openSidebar();
    });
}

if (overlay) {
    overlay.addEventListener('click', closeSidebar);
}