import { createTag, getSpans } from './tag_handler.js';

const input = document.querySelector('input.tag');
const list = document.querySelector('ul.suggestions');

// Holds current fetch request.
let controller;

function addSuggestion(tagName) {
    input.value = null;
    createTag(tagName);

    input.focus();
}

async function handleSuggesting(event) {
    const query = this.value;
    if (controller) controller.abort();
    if (!query.length) return;

    // Setup abort controller.
    controller = new AbortController();
    const signal = controller.signal;

    // Ignore tags that are already specified.
    const ignoreTags = [];

    getSpans().forEach(function(span) {
        ignoreTags.push('-' + span.textContent);
    });

    try {
        const params = new URLSearchParams({
            limit: 10,
            page: 1,
            sort: 'id',
            sort_by: 'desc',
            terms: query
        });
        const response = await fetch(
            `/api/tags?${params.toString()}+${ignoreTags.join('+')}`,
            {
                signal
            }
        );
        const json = await response.json();
        const tags = json['tags'];
        if (!tags.length) return;

        list.innerHTML = null;
        list.style.display = 'block';

        for (let i = 0; i < tags.length; i++) {
            const tagName = tags[i]['name'];

            const li = document.createElement('li');
            li.textContent = tagName;

            list.appendChild(li);

            li.addEventListener('mousedown', addSuggestion.bind(null, tagName));
        }
    } catch (error) {
        if (error.name === 'AbortError') return;
        console.log(`Suggestion error: ${error}`);
    }
}

input.addEventListener('focusin', handleSuggesting);
input.addEventListener('focusout', function() {
    list.innerHTML = '';
    list.style.display = 'none';
});

input.addEventListener('input', handleSuggesting);
