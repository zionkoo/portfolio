const menuButton = document.querySelector('.menu-button');
const siteNav = document.querySelector('.site-nav');

menuButton?.addEventListener('click', () => {
  const open = siteNav.classList.toggle('is-open');
  menuButton.setAttribute('aria-expanded', String(open));
});

siteNav?.querySelectorAll('a').forEach((link) => {
  link.addEventListener('click', () => {
    siteNav.classList.remove('is-open');
    menuButton?.setAttribute('aria-expanded', 'false');
  });
});

const tocLinks = [...document.querySelectorAll('.case-toc a[href^="#"]')];
const observedSections = tocLinks
  .map((link) => document.querySelector(link.getAttribute('href')))
  .filter(Boolean);

if (observedSections.length) {
  const sectionObserver = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) return;
      tocLinks.forEach((link) => {
        link.classList.toggle('is-current', link.getAttribute('href') === `#${entry.target.id}`);
      });
    });
  }, { rootMargin: '-22% 0px -68% 0px' });
  observedSections.forEach((section) => sectionObserver.observe(section));
}

const backTop = document.querySelector('.back-top');
const updateBackTop = () => backTop?.classList.toggle('is-visible', window.scrollY > 700);
window.addEventListener('scroll', updateBackTop, { passive: true });
updateBackTop();

const visitCounter = document.querySelector('#portfolioVisitCounter');
if (visitCounter) {
  const visitEndpoint = 'https://strion-garmin-sync.zionkoo.workers.dev/api/portfolio/views';
  const ownerKey = 'zionkoo_portfolio_owner';
  const countedKey = 'zionkoo_portfolio_view_counted_v1';
  const pageUrl = new URL(window.location.href);
  const shouldRegisterOwner = pageUrl.searchParams.get('owner') === '1';

  if (shouldRegisterOwner) {
    localStorage.setItem(ownerKey, 'true');
    pageUrl.searchParams.delete('owner');
    history.replaceState(null, '', `${pageUrl.pathname}${pageUrl.search}${pageUrl.hash}`);
  }

  const isOwner = localStorage.getItem(ownerKey) === 'true';
  const alreadyCounted = localStorage.getItem(countedKey) === 'true';
  const registerOwner = shouldRegisterOwner
    ? fetch(visitEndpoint.replace('/views', '/owner'), { method: 'POST' }).catch(() => null)
    : Promise.resolve();

  registerOwner
    .then(() => fetch(visitEndpoint, { method: isOwner || alreadyCounted ? 'GET' : 'POST' }))
    .then((response) => {
      if (!response.ok) throw new Error('visit counter unavailable');
      return response.json();
    })
    .then(({ count, isOwner: ownerByIp }) => {
      visitCounter.textContent = `외부 열람 ${Number(count).toLocaleString('ko-KR')}회`;
      visitCounter.hidden = false;
      if (!isOwner && !ownerByIp && !alreadyCounted) localStorage.setItem(countedKey, 'true');
    })
    .catch(() => { visitCounter.hidden = true; });
}
