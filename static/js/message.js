// JavaScript library for messaging.

const messages = document.getElementById('messages');

export function removeMessage(span) {
    /**
     * Removes message.
     * @param {HTMLSpanElement} span - Message to remove.
    */
    span.parentElement.removeChild(span);
}

export function sendMessage(message, removeAfter = true, delay = 3) {
    /**
     * Displays message with additional cleanup ability.
     * @param {string} message - Message to display.
     * @param {boolean} removeAfter - Whether to cleanup the message after a delay.
     * @param {number} delay - Delay after which to cleanup.
    */
    const span = document.createElement('span');
    span.classList.add('message');
    span.classList.add('no-select');

    span.textContent = message;
    messages.appendChild(span);

    if (removeAfter) {
        setTimeout(removeMessage, delay * 1000, span)
    }
}

export function sendErrorMessage(message) {
    /**
     * Displays an error message with delay of 5 seconds.
     * @param {string} message - Message to display.
    */
    return sendMessage(message, true, 5);
}
