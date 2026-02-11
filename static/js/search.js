import { createTag, getTags } from './tag_handler.js';

const searchForm = document.getElementById('search-form');
const interactiveTags = searchForm.getElementsByClassName('interactive-tags')[0];
const input = interactiveTags.querySelector('input.tag');

const currentParams = new URLSearchParams(window.location.href);
const tags = currentParams.get('search').split(' ');

for (let i = 0; i < tags.length; i++) {
    const tagName = tags[i];

    createTag(tagName, interactiveTags, input);
}

searchForm.addEventListener('submit', function(event) {
    event.preventDefault();

    const formData = new FormData(searchForm);
    formData.set('search', getTags(interactiveTags).join(' '));

    const params = new URLSearchParams(formData);

    fetch(`?${params.toString()}`).then(function(response) {
        if (response.ok) {
            window.location.href = response.url;
        }
    });
});
