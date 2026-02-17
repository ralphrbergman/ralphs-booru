/**
 * JavaScript module to show/hide user's API key within /edit_profile page.
*/

const keySpan = document.getElementById('user-api-key');
const apiKey = keySpan.textContent;
const btn = document.getElementById('key-btn');

function hideKey() {
    keySpan.textContent = '*'.repeat(apiKey.length);
    keySpan.style.pointerEvents = 'none';
    keySpan.style.userSelect = 'none';
}

function showKey() {
    keySpan.textContent = apiKey;
    keySpan.style.pointerEvents = 'auto';
    keySpan.style.userSelect = 'text';
}

// Hide the API key by default.
hideKey();

btn.addEventListener('click', function(event) {
    // Don't do anything with the form.
    event.preventDefault();

    const shown = btn.dataset.shown == 'true' ? true : false;
    shown ? hideKey() : showKey();
    const btnText = shown ? 'Show key' : 'Hide key';

    btn.textContent = btnText;
    btn.dataset.shown = !shown;
});
