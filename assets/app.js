const navToggle = document.querySelector('.nav-toggle');
const nav = document.querySelector('#site-nav');

if (navToggle && nav) {
  navToggle.addEventListener('click', () => {
    const isOpen = nav.classList.toggle('is-open');
    navToggle.setAttribute('aria-expanded', String(isOpen));
  });
}

const themeToggle = document.querySelector('.theme-toggle');
const root = document.documentElement;
const storageKey = 'skill-html-theme';
const prefersDark = window.matchMedia('(prefers-color-scheme: dark)');

function systemTheme() {
  return prefersDark.matches ? 'dark' : 'light';
}

function activeTheme() {
  return root.dataset.theme || systemTheme();
}

function updateThemeButton() {
  if (!themeToggle) return;
  const isDark = activeTheme() === 'dark';
  themeToggle.textContent = isDark ? '淺色' : '深色';
  themeToggle.setAttribute('aria-pressed', String(isDark));
  themeToggle.setAttribute('title', isDark ? '切換到淺色模式' : '切換到深色模式');
}

try {
  const savedTheme = localStorage.getItem(storageKey);
  if (savedTheme === 'dark' || savedTheme === 'light') {
    root.dataset.theme = savedTheme;
  }
} catch (_error) {
  // localStorage may be disabled; system color-scheme still works.
}

updateThemeButton();
prefersDark.addEventListener?.('change', updateThemeButton);

if (themeToggle) {
  themeToggle.addEventListener('click', () => {
    const nextTheme = activeTheme() === 'dark' ? 'light' : 'dark';
    root.dataset.theme = nextTheme;
    try {
      localStorage.setItem(storageKey, nextTheme);
    } catch (_error) {
      // Ignore storage failures; the current page still switches theme.
    }
    updateThemeButton();
  });
}

const searchInput = document.querySelector('#skill-search');
const cards = Array.from(document.querySelectorAll('[data-search]'));

if (searchInput && cards.length > 0) {
  searchInput.addEventListener('input', () => {
    const query = searchInput.value.trim().toLowerCase();
    for (const card of cards) {
      const haystack = card.getAttribute('data-search')?.toLowerCase() || '';
      card.classList.toggle('is-hidden', query.length > 0 && !haystack.includes(query));
    }
  });
}
