// JavaScript library for messaging.

const messages = document.getElementById('messages');

export function removeMessage(span) {
    span.parentElement.removeChild(span);
}

export function sendMessage(message, removeAfter = true, delay = 3) {
    const span = document.createElement('span');
    span.classList.add('message');
    span.classList.add('no-select');

    span.textContent = message;
    messages.appendChild(span);

    if (removeAfter) {
        setTimeout(removeMessage, delay * 1000, span)
    }
}
