import { sendMessage, sendErrorMessage } from "./message.js";

const apiKey = document.getElementById('api-key').textContent;
const postForm = document.getElementById('manage-post-form');

// Show the form once JavaScript begins running.
postForm.style.display = 'block';

const toggleBtn = document.getElementById('toggle-btn');
const posts = document.querySelectorAll('.post-container');

// AbortController used to disconnect 'postClick' function.
let controller;

let state = false;
let selectedPosts = [];

function postClick(post) {
    /**
     * Toggle between selected and deselected state for post.
     * @param {HTMLDivElement} post - Post to toggle.
    */

    if (post.classList.contains('deselected')) selectedPosts.push(post);
    else selectedPosts.splice(selectedPosts.indexOf(post), 1);

    post.classList.toggle('deselected');
    post.classList.toggle('selected');
}

function getTags() {
    /** Obtain tags from interactive tags area. */
    const spanTags = postForm.querySelectorAll('span.tag');
    const tagInput = postForm.querySelector('input.tag');

    let tags = [];

    spanTags.forEach(function(span) {
        const Content = span.textContent.trim();
        if (Content.length === 0) return;

        tags.push(Content);
    });

    // Also include tag that's not pushed to a span.
    if (tagInput.value.trim().length > 0) tags.push(tagInput.value.trim());

    return tags;
}

toggleBtn.addEventListener('click', function(event) {
    if (!controller) controller = new AbortController();

    let fn;

    if (state === false) {
        // Turn on post selection mode.
        state = true;

        fn = function(post) {
            // Assign a colored border.
            if (selectedPosts.includes(post)) {
                post.classList.add('selected');
            } else {
                post.classList.add('deselected');
            }

            // Handle toggling within selected posts array.
            post.addEventListener('click', function(event) {
                event.preventDefault();

                postClick(post);
            }, {
                signal: controller.signal
            });
        }
    } else {
        // Turn off post selection.
        state = false;

        fn = function(post) {
            post.classList.remove('selected');
            post.classList.remove('deselected');

            controller.abort();
        }
    }

    // Handle connect/disconnect click event on posts.
    for (let i = 0; i < posts.length; i++) {
        let post = posts[i].parentElement;

        fn(post);
    }

    // Allow for a new AbortController to be born.
    if (!state) {
        controller = null;
    }
});

// Handle form submission.
postForm.addEventListener('submit', function(event) {
    event.preventDefault();

    // Ignore when there are no posts selected for change.
    if (selectedPosts.length === 0) {
        sendErrorMessage('You haven\'t selected any posts.');
        return;
    }

    const Form = new FormData(postForm);

    Form.set('tags', getTags());

    if (Form.get('tags').length === 0) {
        sendErrorMessage('Tags are missing.');
        return;
    }

    // Create the base request object.
    let obj = Object.fromEntries(Form);
    // Split tags into array.
    obj.tags = obj.tags.split(',');

    // Obtain post IDs.
    obj.post_ids = [];

    for (let i = 0; i < selectedPosts.length; i++) {
        let post = selectedPosts[i];
        obj.post_ids.push(parseInt(post.dataset.postId, 10));
    }

    // Select endpoint.
    const added = event.submitter.dataset.value === 'add';
    const endpoint = added ? '/add' : '/remove';

    // Send the request.
    fetch(`/api/tags${endpoint}`, {
        headers: {
            'Authorization': `Bearer ${apiKey}`,
            'Content-Type': 'application/json'
        },
        method: 'PATCH',
        body: JSON.stringify(obj)
    }).then(function(response) {
        if (response.ok) {
            // Message the user.
            const actionText = added ? 'added' : 'removed';

            sendMessage(`Successfully ${actionText} tags: ${obj.tags.join(', ')}`)
        }
    });
});
