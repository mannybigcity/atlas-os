const navToggle = document.querySelector('.nav-toggle');
const siteNav = document.querySelector('.site-nav');
const quoteForm = document.querySelector('#quote-form');
const serviceSelect = document.querySelector('#service');
const leadBrief = document.querySelector('#lead-brief');
const briefOutput = document.querySelector('#brief-output');
const briefChip = document.querySelector('#brief-chip');
const copyBrief = document.querySelector('#copy-brief');
const downloadBrief = document.querySelector('#download-brief');
const revealItems = document.querySelectorAll('.reveal');
const parallaxItems = document.querySelectorAll('.parallax-card, .parallax-media');
const magneticItems = document.querySelectorAll('.magnetic');

let latestBrief = '';
let ticking = false;
let reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

if (navToggle && siteNav) {
  navToggle.addEventListener('click', () => {
    const isOpen = siteNav.classList.toggle('is-open');
    navToggle.setAttribute('aria-expanded', String(isOpen));
  });

  siteNav.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', () => {
      siteNav.classList.remove('is-open');
      navToggle.setAttribute('aria-expanded', 'false');
    });
  });
}

document.querySelectorAll('[data-interest]').forEach(link => {
  link.addEventListener('click', () => {
    const interest = link.getAttribute('data-interest');
    if (!interest || !serviceSelect) return;

    const matchingOption = Array.from(serviceSelect.options).find(option => {
      return option.textContent.trim().toLowerCase() === interest.trim().toLowerCase();
    });

    if (matchingOption) {
      serviceSelect.value = matchingOption.value || matchingOption.textContent;
    }
  });
});

function formPayload(form) {
  return Object.fromEntries(Array.from(new FormData(form).entries()).map(([key, value]) => {
    return [key, String(value).trim()];
  }));
}

function localLeadBrief(payload, saved = false, leadId = 'local-draft') {
  return [
    'AMANDA WEBSITE LEAD BRIEF',
    `Lead ID: ${leadId}`,
    `Capture status: ${saved ? 'Saved to PUTER backend' : 'Draft generated in browser fallback'}`,
    `Name: ${payload.Name || 'Not provided'}`,
    `Organization: ${payload.Organization || 'Not provided'}`,
    `Email: ${payload.Email || 'Not provided'}`,
    `Phone: ${payload.Phone || 'Not provided'}`,
    `Service: ${payload.Service || 'Not provided'}`,
    `Quantity / group size: ${payload.Quantity || 'Not provided'}`,
    `Needed by: ${payload['Needed By'] || 'Not provided'}`,
    `Artwork status: ${payload['Artwork Status'] || 'Not provided'}`,
    `Preferred contact: ${payload['Preferred Contact'] || 'Not provided'}`,
    `Best contact time: ${payload['Best Contact Time'] || 'Not provided'}`,
    `Decision stage: ${payload['Decision Stage'] || 'Not provided'}`,
    `Timeline pressure: ${payload['Timeline Pressure'] || 'Not provided'}`,
    `Project details: ${payload['Project Details'] || 'Not provided'}`,
    'Next step: Amanda follows up with quote-ready questions and confirms timeline feasibility.'
  ].join('\n');
}

function showBrief(brief, saved = false) {
  latestBrief = brief;
  if (briefOutput) briefOutput.textContent = brief;
  if (briefChip) briefChip.textContent = saved ? 'Saved lead' : 'Lead brief';
  if (leadBrief) leadBrief.hidden = false;
}

async function submitLead(payload) {
  const response = await fetch('/api/website-leads', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });

  const result = await response.json().catch(() => ({}));
  if (!response.ok || !result.success) {
    throw new Error(result.error || 'Lead endpoint unavailable');
  }

  return result;
}

if (quoteForm) {
  quoteForm.addEventListener('submit', async event => {
    event.preventDefault();

    if (!quoteForm.checkValidity()) {
      quoteForm.reportValidity();
      return;
    }

    const button = quoteForm.querySelector('button[type="submit"]');
    const payload = formPayload(quoteForm);
    const originalButtonText = button ? button.textContent : '';

    if (button) {
      button.disabled = true;
      button.textContent = 'Capturing Lead...';
    }

    try {
      const result = await submitLead(payload);
      showBrief(result.brief || localLeadBrief(payload, true, result.lead_id), true);
      if (button) button.textContent = 'Lead Saved for Amanda';
    } catch (error) {
      const fallbackId = `draft-${Date.now()}`;
      window.localStorage?.setItem(`sis-lead-${fallbackId}`, JSON.stringify({ id: fallbackId, payload, captured_at: new Date().toISOString() }));
      showBrief(localLeadBrief(payload, false, fallbackId), false);
      if (button) button.textContent = 'Draft Created — Copy or Download';
    } finally {
      if (button) {
        setTimeout(() => {
          button.disabled = false;
          button.textContent = originalButtonText;
        }, 2400);
      }
    }
  });
}

if (copyBrief) {
  copyBrief.addEventListener('click', async () => {
    if (!latestBrief) return;
    try {
      await navigator.clipboard.writeText(latestBrief);
      copyBrief.textContent = 'Copied';
      setTimeout(() => { copyBrief.textContent = 'Copy brief'; }, 1500);
    } catch (error) {
      briefOutput?.focus();
    }
  });
}

if (downloadBrief) {
  downloadBrief.addEventListener('click', () => {
    if (!latestBrief) return;
    const blob = new Blob([latestBrief], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `sis-amanda-lead-${Date.now()}.txt`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
  });
}

if ('IntersectionObserver' in window) {
  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-visible');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.01, rootMargin: '420px 0px 420px 0px' });

  revealItems.forEach((item, index) => {
    item.style.setProperty('--reveal-delay', `${Math.min(index % 4, 3) * 80}ms`);
    observer.observe(item);
  });

  window.requestAnimationFrame(() => {
    revealItems.forEach(item => {
      const rect = item.getBoundingClientRect();
      if (rect.top < window.innerHeight + 420) item.classList.add('is-visible');
    });
  });

  setTimeout(() => {
    revealItems.forEach(item => item.classList.add('is-visible'));
  }, 1400);
} else {
  revealItems.forEach(item => item.classList.add('is-visible'));
}

function updateParallax() {
  ticking = false;
  if (reducedMotion) return;

  const viewportHeight = window.innerHeight || 1;

  parallaxItems.forEach(item => {
    const rect = item.getBoundingClientRect();
    if (rect.bottom < -120 || rect.top > viewportHeight + 120) return;

    const speed = Number(item.dataset.parallaxSpeed || 0.08);
    const progress = (rect.top + rect.height / 2 - viewportHeight / 2) / viewportHeight;
    const y = progress * speed * -160;
    item.style.setProperty('--parallax-y', `${y.toFixed(2)}px`);

    if (item.classList.contains('parallax-media')) {
      item.style.transform = `translate3d(0, ${y.toFixed(2)}px, 0)`;
    } else {
      item.style.transform = `translate3d(0, ${y.toFixed(2)}px, 0)`;
    }
  });
}

function requestParallax() {
  if (!ticking) {
    ticking = true;
    window.requestAnimationFrame(updateParallax);
  }
}

window.addEventListener('scroll', requestParallax, { passive: true });
window.addEventListener('resize', requestParallax);
window.addEventListener('load', requestParallax);
requestParallax();

magneticItems.forEach(item => {
  item.addEventListener('pointermove', event => {
    if (reducedMotion) return;
    const rect = item.getBoundingClientRect();
    const x = event.clientX - rect.left - rect.width / 2;
    const y = event.clientY - rect.top - rect.height / 2;
    item.style.transform = `translate3d(${(x * 0.08).toFixed(2)}px, ${(y * 0.12).toFixed(2)}px, 0)`;
  });

  item.addEventListener('pointerleave', () => {
    item.style.transform = '';
  });
});
