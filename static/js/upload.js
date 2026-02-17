const postForm = document.getElementById('post-form');
const interactiveTags = document.getElementsByClassName('interactive-tags')[0];
const tagInput = interactiveTags.querySelector('input.tag');

// Handle form submission.
postForm.addEventListener('submit', function(event) {
    event.preventDefault();

    let tags = [];

    // Collect tags from all spans.
    document.querySelectorAll('span.tag').forEach(span => {
        const Text = span.textContent.trim();
        if (Text) tags.push(Text);
    });

    // Add the current value in the input box if the user didn't hit space.
    if (tagInput.value.trim()) {
        tags.push(tagInput.value.trim());
    }

    // Construct a form.
    let data = new FormData(postForm);
    
    data.set('tags', tags.join(' '));

    // Send the request.
    fetch(window.location.href, {
        method: 'POST',
        body: data
    })
    .then(function (response) {
        if (response.redirected) {
            window.location.href = response.url;
        } else if (response.ok) {
            window.location.reload();
        }
    })
});
