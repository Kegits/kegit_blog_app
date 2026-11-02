document.addEventListener('error', (event) => {
  const image = event.target;
  if (!(image instanceof HTMLImageElement) || !image.dataset.fallbackUrl || image.dataset.fallbackApplied) {
    return;
  }

  image.dataset.fallbackApplied = 'true';
  image.src = image.dataset.fallbackUrl;
}, true);

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
