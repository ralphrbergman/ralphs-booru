import { createTag, getSpans } from './tag_handler.js';

// Holds current fetch request abort controller.
let controller;

function addSuggestion(input, tagName) {
    /**
     * Adds suggestion to tag area.
     * @param {HTMLInputElement} input - Input element to reset.
     * @param {string} tagName - Tag to add.
    */
    input.value = null;
    createTag(tagName, input.parentElement.parentElement, input);
}

async function handleSuggesting(input, list) {
    /**
     * Adds handling of suggestions to an input element.
     * @param {HTMLInputElement} input - Input element to add suggestions to.
     * @param {HTMLUListElement} list - List element to hold suggestions.
    */
    const query = input.value;

    if (controller) controller.abort();
    if (!query.length) return;

    // Setup abort controller.
    controller = new AbortController();

    // Ignore tags that are already specified.
    const ignoreTags = [];

    getSpans(input.parentElement.parentElement).forEach(function(span) {
        ignoreTags.push('-' + span.textContent);
    });

    try {
        const params = new URLSearchParams({
            limit: 10,
            page: 1,
            sort: 'name',
            sort_by: 'desc',
            terms: query
        });

        // Make the request for suggestions.
        const response = await fetch(
            `/api/tags?${params.toString()}+${ignoreTags.join('+')}`,
            {
                signal: controller.signal
            }
        ).then(async function(response) {
            const json = await response.json();
            const tags = json['tags'];
            if (!tags.length) return;

            // Display the suggestions.
            list.innerHTML = null;
            list.style.display = 'block';

            for (let i = 0; i < tags.length; i++) {
                const tagName = tags[i]['name'];

                const li = document.createElement('li');
                li.textContent = tagName;

                list.appendChild(li);

                li.addEventListener(
                    'mousedown',
                    addSuggestion.bind(null, input, tagName)
                );
            }
        });
    } catch (error) {
        if (error.name === 'AbortError') return;
        console.log(`Suggestion error: ${error}`);
    }
}

// Handle registering suggestion feature to input elements.
const inputs = document.querySelectorAll('input.tag');

inputs.forEach(function(input) {
    const list = input.nextElementSibling;

    input.addEventListener('focusin', handleSuggesting.bind(null, input, list));
    input.addEventListener('focusout', function() {
        list.innerHTML = '';
        list.style.display = 'none';
    });

    input.addEventListener('input', handleSuggesting.bind(null, input, list));
});
