const menuButton = document.querySelector('.menu-button');
const mainNav = document.querySelector('#main-nav');
const seedStage = document.querySelector('#seed-stage');
const quoteForm = document.querySelector('#quote-form');
const leadBrief = document.querySelector('#lead-brief');
const briefOutput = document.querySelector('#brief-output');
const briefChip = document.querySelector('#brief-chip');
const copyBrief = document.querySelector('#copy-brief');
const downloadBrief = document.querySelector('#download-brief');
const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

let latestBrief = '';

if (!reduceMotion) {
  document.body.classList.add('has-motion');
}

function showMissingAsset(image) {
  const source = image.getAttribute('src') || 'unknown asset';
  const replacement = document.createElement('div');
  replacement.className = 'missing-asset';
  replacement.setAttribute('role', 'img');
  replacement.setAttribute('aria-label', `Missing Asset: ${source}`);
  replacement.innerHTML = `Missing Asset<span>${source}</span>`;
  image.replaceWith(replacement);
}

document.querySelectorAll('img').forEach((image) => {
  if (image.complete && image.naturalWidth === 0) showMissingAsset(image);
  image.addEventListener('error', () => showMissingAsset(image), { once: true });
});

document.querySelectorAll('.etsy-link').forEach((link) => {
  const configuredUrl = (link.dataset.etsyUrl || '').trim();
  if (!configuredUrl) {
    link.classList.add('needs-config');
    link.addEventListener('click', (event) => {
      event.preventDefault();
      document.querySelector('#etsy-needed')?.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    return;
  }

  link.href = configuredUrl;
  link.target = '_blank';
  link.rel = 'noopener noreferrer';
});

function closeMenu() {
  if (!menuButton || !mainNav) return;
  mainNav.classList.remove('open');
  menuButton.setAttribute('aria-expanded', 'false');
  document.body.classList.remove('menu-open');
}

if (menuButton && mainNav) {
  menuButton.addEventListener('click', () => {
    const isOpen = mainNav.classList.toggle('open');
    menuButton.setAttribute('aria-expanded', String(isOpen));
    document.body.classList.toggle('menu-open', isOpen && window.innerWidth < 980);
  });

  mainNav.querySelectorAll('a').forEach((link) => link.addEventListener('click', closeMenu));
}

const seedAssets = [
  'assets/sis-dandelion-seed-3d-transparent.svg'
];

const seedFlightPlan = [
  { left: 4, start: '-10vw', sway: '24vw', time: '34s', delay: '-7s', scale: 1.08, tilt: '-18deg' },
  { left: 16, start: '-4vw', sway: '16vw', time: '29s', delay: '-22s', scale: 0.84, tilt: '21deg' },
  { left: 27, start: '2vw', sway: '31vw', time: '38s', delay: '-14s', scale: 1.18, tilt: '-32deg' },
  { left: 38, start: '-7vw', sway: '18vw', time: '31s', delay: '-29s', scale: 0.92, tilt: '13deg' },
  { left: 48, start: '8vw', sway: '-20vw', time: '36s', delay: '-4s', scale: 1.26, tilt: '-8deg' },
  { left: 60, start: '-5vw', sway: '22vw', time: '33s', delay: '-18s', scale: 0.88, tilt: '27deg' },
  { left: 69, start: '4vw', sway: '-15vw', time: '40s', delay: '-31s', scale: 1.12, tilt: '-24deg' },
  { left: 81, start: '7vw', sway: '-28vw', time: '35s', delay: '-11s', scale: 0.96, tilt: '18deg' },
  { left: 91, start: '-2vw', sway: '-19vw', time: '42s', delay: '-25s', scale: 1.32, tilt: '-14deg' },
  { left: 12, start: '6vw', sway: '26vw', time: '44s', delay: '-36s', scale: 1.2, tilt: '34deg' },
  { left: 53, start: '-12vw', sway: '12vw', time: '39s', delay: '-34s', scale: 1.02, tilt: '-28deg' },
  { left: 74, start: '-6vw', sway: '20vw', time: '37s', delay: '-2s', scale: 0.9, tilt: '7deg' }
];

function buildSeeds() {
  if (!seedStage || reduceMotion) return;
  const count = window.innerWidth < 720 ? 7 : seedFlightPlan.length;
  seedStage.innerHTML = '';

  seedFlightPlan.slice(0, count).forEach((settings, index) => {
    const seed = document.createElement('img');
    seed.className = 'seed';
    seed.src = seedAssets[index % seedAssets.length];
    seed.alt = '';
    seed.decoding = 'async';
    seed.style.left = `${settings.left}%`;
    seed.style.setProperty('--start', settings.start);
    seed.style.setProperty('--sway', settings.sway);
    seed.style.setProperty('--time', settings.time);
    seed.style.setProperty('--delay', settings.delay);
    seed.style.setProperty('--scale', settings.scale);
    seed.style.setProperty('--tilt', settings.tilt);
    seedStage.appendChild(seed);
  });
}

buildSeeds();
window.addEventListener('resize', () => {
  window.clearTimeout(window.__sisSeedResize);
  window.__sisSeedResize = window.setTimeout(buildSeeds, 220);
});

function readForm(form) {
  return Object.fromEntries(Array.from(new FormData(form).entries()).map(([key, value]) => [key, String(value).trim()]));
}

function createBrief(payload, saved = false, leadId = 'browser-draft') {
  return [
    'SIS CUSTOM CREATIONS LEAD BRIEF',
    `Lead ID: ${leadId}`,
    `Capture status: ${saved ? 'Saved to PUTER backend' : 'Draft created in browser fallback'}`,
    '',
    `Name: ${payload.Name || 'Not provided'}`,
    `Email: ${payload.Email || 'Not provided'}`,
    `Phone: ${payload.Phone || 'Not provided'}`,
    `Experience / product: ${payload.Service || 'Not provided'}`,
    `Desired date: ${payload['Needed By'] || 'Not provided'}`,
    `Guest count / quantity: ${payload.Quantity || 'Not provided'}`,
    '',
    'What this moment should become:',
    payload['Project Details'] || 'Not provided',
    '',
    'Why it matters: SIS is built around Deleana’s purpose to create meaningful experiences, bring people together, make lasting memories, and build a family legacy.',
    'Next step: Amanda follows up with quote-ready questions and keeps the Create. Connect. Celebrate. promise clear.'
  ].join('\n');
}

function showBrief(brief, saved) {
  latestBrief = brief;
  if (briefOutput) briefOutput.textContent = brief;
  if (briefChip) briefChip.textContent = saved ? 'Saved lead' : 'Lead brief';
  if (leadBrief) leadBrief.hidden = false;
}

async function saveLead(payload) {
  const response = await fetch('/api/website-leads', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  const result = await response.json().catch(() => ({}));
  if (!response.ok || !result.success) throw new Error(result.error || 'Lead endpoint unavailable');
  return result;
}

if (quoteForm) {
  quoteForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    if (!quoteForm.checkValidity()) {
      quoteForm.reportValidity();
      return;
    }

    const payload = readForm(quoteForm);
    const button = quoteForm.querySelector('button[type="submit"]');
    const originalText = button?.textContent || 'Create lead brief';

    if (button) {
      button.disabled = true;
      button.textContent = 'Creating SIS brief...';
    }

    try {
      const result = await saveLead(payload);
      showBrief(result.brief || createBrief(payload, true, result.lead_id), true);
      if (button) button.textContent = 'Lead saved';
    } catch (error) {
      const fallbackId = `sis-draft-${Date.now()}`;
      window.localStorage?.setItem(fallbackId, JSON.stringify({ payload, captured_at: new Date().toISOString() }));
      showBrief(createBrief(payload, false, fallbackId), false);
      if (button) button.textContent = 'Draft created';
    } finally {
      if (button) {
        window.setTimeout(() => {
          button.disabled = false;
          button.textContent = originalText;
        }, 2200);
      }
    }
  });
}

copyBrief?.addEventListener('click', async () => {
  if (!latestBrief) return;
  try {
    await navigator.clipboard.writeText(latestBrief);
    copyBrief.textContent = 'Copied';
    window.setTimeout(() => { copyBrief.textContent = 'Copy'; }, 1400);
  } catch (error) {
    briefOutput?.focus();
  }
});

downloadBrief?.addEventListener('click', () => {
  if (!latestBrief) return;
  const blob = new Blob([latestBrief], { type: 'text/plain' });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = `sis-lead-brief-${Date.now()}.txt`;
  document.body.append(anchor);
  anchor.click();
  anchor.remove();
  URL.revokeObjectURL(url);
});

const revealItems = document.querySelectorAll('.reveal');
if ('IntersectionObserver' in window && !reduceMotion) {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12, rootMargin: '0px 0px -6% 0px' });
  revealItems.forEach((item) => observer.observe(item));
} else {
  revealItems.forEach((item) => item.classList.add('visible'));
}
