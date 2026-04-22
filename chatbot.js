(function () {
  const messages = [];
  let isOpen = false;
  let isLoading = false;

  // ── Inject HTML ──────────────────────────────────────────────
  const widget = document.createElement('div');
  widget.id = 'st-chatbot';
  widget.innerHTML = `
    <button id="st-chat-toggle" aria-label="Open AI consultant chat">
      <svg id="st-icon-chat" xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
        <path stroke-linecap="round" stroke-linejoin="round" d="M8 10h.01M12 10h.01M16 10h.01M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2v10z"/>
      </svg>
      <svg id="st-icon-close" xmlns="http://www.w3.org/2000/svg" width="22" height="22" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" style="display:none">
        <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/>
      </svg>
    </button>
    <div id="st-chat-panel" aria-live="polite">
      <div id="st-chat-header">
        <div id="st-chat-header-info">
          <div id="st-chat-avatar">AI</div>
          <div>
            <div id="st-chat-name">Strong Tower AI</div>
            <div id="st-chat-status">AI Consultant</div>
          </div>
        </div>
      </div>
      <div id="st-chat-messages"></div>
      <div id="st-chat-input-row">
        <input id="st-chat-input" type="text" placeholder="Type your message..." autocomplete="off" maxlength="500" />
        <button id="st-chat-send" aria-label="Send message">
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M22 2L11 13M22 2L15 22l-4-9-9-4 20-7z"/>
          </svg>
        </button>
      </div>
    </div>
  `;
  document.body.appendChild(widget);

  // ── Element refs ─────────────────────────────────────────────
  const toggle     = document.getElementById('st-chat-toggle');
  const panel      = document.getElementById('st-chat-panel');
  const msgList    = document.getElementById('st-chat-messages');
  const input      = document.getElementById('st-chat-input');
  const sendBtn    = document.getElementById('st-chat-send');
  const iconChat   = document.getElementById('st-icon-chat');
  const iconClose  = document.getElementById('st-icon-close');

  // ── Open / close ─────────────────────────────────────────────
  function openChat() {
    isOpen = true;
    panel.classList.add('open');
    iconChat.style.display = 'none';
    iconClose.style.display = 'block';
    input.focus();
    if (messages.length === 0) initConversation();
  }

  function closeChat() {
    isOpen = false;
    panel.classList.remove('open');
    iconChat.style.display = 'block';
    iconClose.style.display = 'none';
  }

  toggle.addEventListener('click', () => isOpen ? closeChat() : openChat());

  // ── Render a message bubble ──────────────────────────────────
  function appendMessage(role, text) {
    const wrap = document.createElement('div');
    wrap.className = `st-msg st-msg-${role}`;
    wrap.textContent = text;
    msgList.appendChild(wrap);
    msgList.scrollTop = msgList.scrollHeight;
  }

  function showTyping() {
    const wrap = document.createElement('div');
    wrap.className = 'st-msg st-msg-assistant st-typing';
    wrap.id = 'st-typing';
    wrap.innerHTML = '<span></span><span></span><span></span>';
    msgList.appendChild(wrap);
    msgList.scrollTop = msgList.scrollHeight;
  }

  function removeTyping() {
    const el = document.getElementById('st-typing');
    if (el) el.remove();
  }

  // ── Call the serverless function ─────────────────────────────
  async function sendToAPI() {
    showTyping();
    setInputDisabled(true);

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ messages }),
      });

      const data = await res.json();
      removeTyping();

      if (!res.ok) throw new Error(data.error || 'Request failed');

      const reply = data.content;
      messages.push({ role: 'assistant', content: reply });
      appendMessage('assistant', reply);
    } catch (err) {
      removeTyping();
      appendMessage('assistant', "Sorry, something went wrong on my end. Please try again in a moment.");
    } finally {
      setInputDisabled(false);
      input.focus();
    }
  }

  // ── Kick off the conversation ────────────────────────────────
  async function initConversation() {
    messages.push({ role: 'user', content: 'Hello' });
    await sendToAPI();
  }

  // ── Handle user sending a message ───────────────────────────
  function handleSend() {
    const text = input.value.trim();
    if (!text || isLoading) return;
    input.value = '';
    messages.push({ role: 'user', content: text });
    appendMessage('user', text);
    sendToAPI();
  }

  sendBtn.addEventListener('click', handleSend);
  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend(); }
  });

  function setInputDisabled(disabled) {
    isLoading = disabled;
    input.disabled = disabled;
    sendBtn.disabled = disabled;
  }
})();
