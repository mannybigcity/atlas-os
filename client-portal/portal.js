const portalContent = document.getElementById('portalContent');
const lockedContent = document.getElementById('lockedContent');
const session = typeof atlasGetSession === 'function' ? atlasGetSession() : null;
const hasAccess = session && (session.role === 'admin' || session.clientSlug === 'qtime-productions');

if (hasAccess) {
  document.body.classList.remove('locked');
  portalContent.hidden = false;
  lockedContent.hidden = true;
} else {
  document.body.classList.add('locked');
  portalContent.hidden = true;
  lockedContent.hidden = false;
}

document.getElementById('logoutButton')?.addEventListener('click', () => {
  if (typeof atlasLogout === 'function') {
    atlasLogout();
    return;
  }
  sessionStorage.removeItem('atlasClientPortalSession');
  window.location.href = '../client-sign-in/';
});

const responses = [
  {
    match: ['first', 'priority', 'work on first', 'start'],
    answer: 'Start with the sponsor outreach list. The approved blueprint names predictable lead generation and sponsorship outreach as the biggest opportunities, so the highest-value first move is building a targeted list of 100 sponsor-fit companies.'
  },
  {
    match: ['lead', 'leads', 'customers', 'prospects', 'generate more leads'],
    answer: 'To generate more leads, focus on three low-cost channels first: sponsor-fit prospecting, local partnerships, and consistent sponsor-friendly content. Track every conversation in the CRM stages: Prospect, Contacted, Meeting, Proposal, Partner.'
  },
  {
    match: ['score', 'health', '5.2'],
    answer: 'Your Business Health Score is a quick dashboard view from the blueprint: Branding 8/10, Marketing 6/10, Website 5/10, Revenue 4/10, Systems 3/10. The score means the brand foundation is strong, but revenue systems and follow-up systems need attention first.'
  },
  {
    match: ['week', 'next steps', 'next step', 'next priorities', 'priorities'],
    answer: 'Your next priorities are: 1) build the sponsor outreach list, 2) refresh the website message for sponsors, 3) choose a simple CRM pipeline, and 4) gather approved images or links for the digital presence area.'
  },
  {
    match: ['blueprint', 'file', 'pdf'],
    answer: 'The approved QTime Business Growth Blueprint is available in the Blueprint Access card and Files area. V1 only links approved demo files; private client files should wait for server-side authentication.'
  },
  {
    match: ['welcome', 'onboarding', 'approval', 'approvals'],
    answer: 'Use the Welcome, Onboarding, and Approvals links at the top of this portal. Debbie owns the welcome/onboarding experience, and approvals protect Manny and Quincy before anything public is published.'
  }
];

function atlasReply(question) {
  const normalized = question.toLowerCase();
  const found = responses.find(item => item.match.some(term => normalized.includes(term)));
  if (found) return found.answer;
  return 'For V1, this static Atlas Chat demo can answer dashboard questions about priorities, leads, Business Health Score, blueprint files, welcome/onboarding, approvals, and next steps. For anything deeper, Manny should approve live AI/backend integration before client data is sent to an API.';
}

function appendMessage(role, text) {
  const chatMessages = document.getElementById('chatMessages');
  const message = document.createElement('div');
  message.className = `chat-message ${role}`;
  message.innerHTML = `<strong>${role === 'atlas' ? 'Atlas' : 'You'}</strong><span></span>`;
  message.querySelector('span').textContent = text;
  chatMessages.appendChild(message);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

document.querySelectorAll('.prompt-chips button').forEach(button => {
  button.addEventListener('click', () => {
    const text = button.textContent.trim();
    document.getElementById('chatInput').value = text;
    document.getElementById('chatForm').requestSubmit();
  });
});

document.getElementById('chatForm')?.addEventListener('submit', (event) => {
  event.preventDefault();
  const input = document.getElementById('chatInput');
  const question = input.value.trim();
  if (!question) return;
  appendMessage('user', question);
  appendMessage('atlas', atlasReply(question));
  input.value = '';
});
