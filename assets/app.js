const navToggle = document.querySelector('.nav-toggle');
const nav = document.querySelector('#site-nav');

if (navToggle && nav) {
  navToggle.addEventListener('click', () => {
    const isOpen = nav.classList.toggle('is-open');
    navToggle.setAttribute('aria-expanded', String(isOpen));
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
