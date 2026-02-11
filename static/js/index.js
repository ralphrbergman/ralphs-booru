import { getTags } from "./tag_handler.js";

const interactiveTags = document.getElementsByClassName('interactive-tags')[0];
const searchForm = document.getElementById('search-form');

searchForm.addEventListener('submit', function(event) {
    event.preventDefault();

    const formData = new FormData(searchForm);
    formData.set('search', getTags(interactiveTags).join(' '));
    console.log(formData.get('search'));

    const params = new URLSearchParams(formData);

    try {
        const response = fetch(`?${params.toString()}`).then(function(response) {
            if (response.ok && response.redirected) {
                window.location.href = response.url;
            }
        });
    } catch (error) {}
});
