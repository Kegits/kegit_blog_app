document.addEventListener('error', (event) => {
  const image = event.target;
  if (!(image instanceof HTMLImageElement) || !image.dataset.fallbackUrl || image.dataset.fallbackApplied) {
    return;
  }

  image.dataset.fallbackApplied = 'true';
  image.src = image.dataset.fallbackUrl;
}, true);

function addPasswordVisibilityToggles() {
  document.querySelectorAll('input[type="password"]').forEach((input) => {
    if (input.dataset.visibilityToggleInitialized) {
      return;
    }

    input.dataset.visibilityToggleInitialized = 'true';
    const wrapper = document.createElement('div');
    wrapper.className = 'password-input-wrapper';
    input.parentNode.insertBefore(wrapper, input);
    wrapper.append(input);

    const toggle = document.createElement('button');
    toggle.className = 'password-visibility-toggle';
    toggle.type = 'button';
    toggle.innerHTML = '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7S2 12 2 12Z"></path><circle cx="12" cy="12" r="3"></circle><path class="password-visibility-slash" d="m4 4 16 16"></path></svg>';
    toggle.setAttribute('aria-label', 'Show password');
    toggle.setAttribute('aria-pressed', 'false');
    toggle.addEventListener('click', () => {
      const showPassword = input.type === 'password';
      input.type = showPassword ? 'text' : 'password';
      toggle.classList.toggle('password-visible', showPassword);
      toggle.setAttribute('aria-label', `${showPassword ? 'Hide' : 'Show'} password`);
      toggle.setAttribute('aria-pressed', String(showPassword));
    });
    wrapper.append(toggle);
  });
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', addPasswordVisibilityToggles);
} else {
  addPasswordVisibilityToggles();
}

async function loadConversationPreview(details) {
  const content = details.querySelector('[data-comments-content]');
  if (!content || details.dataset.loaded || details.dataset.loading) {
    return;
  }

  details.dataset.loading = 'true';
  content.textContent = 'Loading the latest replies…';
  try {
    const response = await fetch(details.dataset.commentsUrl, {
      credentials: 'same-origin',
      headers: { 'X-Requested-With': 'XMLHttpRequest' },
    });
    if (!response.ok) {
      throw new Error(`Conversation preview request failed (${response.status}).`);
    }

    content.innerHTML = await response.text();
    details.dataset.loaded = 'true';
  } catch (error) {
    console.error('Unable to load the conversation preview.', error);
    const message = document.createElement('p');
    message.className = 'comments-empty';
    message.textContent = 'Could not load replies. Please try again.';
    const retry = document.createElement('button');
    retry.className = 'conversation-retry';
    retry.type = 'button';
    retry.dataset.retryConversation = '';
    retry.textContent = 'Retry';
    content.replaceChildren(message, retry);
  } finally {
    delete details.dataset.loading;
  }
}

document.addEventListener('toggle', (event) => {
  const details = event.target;
  if (details instanceof HTMLDetailsElement && details.matches('.post-conversation') && details.open) {
    loadConversationPreview(details);
  }
}, true);

document.addEventListener('click', (event) => {
  if (!(event.target instanceof Element)) {
    return;
  }
  const retry = event.target.closest('[data-retry-conversation]');
  if (retry) {
    const details = retry.closest('.post-conversation');
    if (details) {
      loadConversationPreview(details);
    }
  }
});
