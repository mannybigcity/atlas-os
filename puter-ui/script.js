const chatForm = document.getElementById('chatForm');
const chatInput = document.getElementById('chatInput');
const chatWindow = document.getElementById('chatWindow');
const micButton = document.getElementById('micButton');

const appendMessage = (text, sender) => {
  const message = document.createElement('div');
  message.className = `message ${sender}`;
  message.innerHTML = `
    <span class="message-label">${sender === 'assistant' ? 'PUTER' : 'You'}</span>
    <p>${text}</p>
  `;
  chatWindow.appendChild(message);
  chatWindow.scrollTop = chatWindow.scrollHeight;
};

chatForm.addEventListener('submit', (event) => {
  event.preventDefault();
  const text = chatInput.value.trim();
  if (!text) return;

  appendMessage(text, 'user');
  chatInput.value = '';

  setTimeout(() => {
    appendMessage('Processing your request... PUTER will answer shortly.', 'assistant');
  }, 600);
});

micButton.addEventListener('click', () => {
  appendMessage('Voice input is not enabled in this preview. Use text commands.', 'assistant');
});
