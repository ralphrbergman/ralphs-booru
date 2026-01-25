const ApiKey = document.getElementById('api-key').textContent;
const PostForm = document.getElementById('manage-post-form');
PostForm.style.display = 'block';

const ToggleBtn = document.getElementById('toggle-btn');
const Posts = document.querySelectorAll('.post-container');

// AbortController used to disconnect 'postClick' function.
let controller;

let state = false;
let selectedPosts = [];

function postClick(post) {
    if (post.classList.contains('deselected')) {
        post.classList.add('selected');
        post.classList.remove('deselected');

        selectedPosts.push(post);
    } else {
        post.classList.add('deselected');
        post.classList.remove('selected');

        selectedPosts.splice(selectedPosts.indexOf(post), 1);
    }
}

function getTags() {
    let tags = [];
    const SpanTags = document.querySelectorAll('span.tag');
    const TagInput = document.querySelector('input.tag');

    SpanTags.forEach(function(span) {
        const Content = span.textContent.trim();
        if (Content.length === 0) return;

        tags.push(Content);
    });

    if (TagInput.value.trim().length > 0) tags.push(TagInput.value.trim());

    return tags;
}

ToggleBtn.addEventListener('click', function(event) {
    if (!controller) controller = new AbortController();

    if (state === false) {
        state = true;

        function fn(post) {
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
        state = false;

        function fn(post) {
            post.classList.remove('selected');
            post.classList.remove('deselected');

            controller.abort();
        }
    }

    // Connect/Disconnect click event on posts.
    for (let i = 0; i < Posts.length; i++) {
        let post = Posts[i].parentElement;

        fn(post);
    }

    // Allow for a new AbortController to be born.
    if (!state) {
        controller = null;
    }
});

// Handle form submission.
PostForm.addEventListener('submit', function(event) {
    event.preventDefault();

    const Form = new FormData(PostForm);

    Form.set('tags', getTags());
    if (Form.get('tags').length === 0) return;

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

    const Endpoint = event.submitter.dataset.value === 'add' ? '/add' : '/remove';

    fetch(`/api/tags${Endpoint}`, {
        headers: {
            'Authorization': `Bearer ${ApiKey}`,
            'Content-Type': 'application/json'
        },
        method: 'PATCH',
        body: JSON.stringify(obj)
    })
});
