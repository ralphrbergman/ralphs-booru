{
    const PostForm = document.getElementById('post-form');
    const InteractiveTags = document.getElementById('interactive-tags');
    const TagInput = InteractiveTags.querySelector('input.tag');

    // Handle form submission.
    PostForm.addEventListener('submit', function(event) {
        event.preventDefault();

        let tags = [];

        // Collect tags from all spans.
        document.querySelectorAll('span.tag').forEach(span => {
            const Text = span.textContent.trim();
            if (Text) tags.push(Text);
        });

        // Add the current value in the input box if the user didn't hit space.
        if (TagInput.value.trim()) {
            tags.push(TagInput.value.trim());
        }

        // Construct a form.
        let data = new FormData(PostForm);
        
        data.set('tags', tags.join(' '));

        fetch(window.location.href, {
            method: 'POST',
            body: data
        })
        .then(response => {
            if (response.redirected) {
                window.location.href = response.url;
            } else if (response.ok) {
                window.location.reload();
            }
        })
    });
}