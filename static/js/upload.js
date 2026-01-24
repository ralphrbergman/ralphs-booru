const PostId = document.getElementById('post-id').textContent.trim();

const PostForm = document.getElementById('post-form');
const InteractiveTags = document.getElementById('interactive-tags');

// Show the interactive tag area, the other one is automatically hidden.
if (InteractiveTags) {
    InteractiveTags.classList.remove('hidden');
    InteractiveTags.style.display = 'flex';
}

function manageSpan(span) {
    function handleSpan(event) {
        if (span.textContent.trim().length === 0) {
            span.remove();
        }
    }

    span.addEventListener('keyup', function(event) {
        handleSpan(event);
    });

    span.addEventListener('focusout', function(event) {
        handleSpan(event);
    });
}

const SpanTags = document.querySelectorAll('span.tag');

SpanTags.forEach(function(span) {
    manageSpan(span);
});

// Handle creating new tags.
const TagInput = InteractiveTags.querySelector('input.tag');

TagInput.addEventListener('keydown', function(event) {
    if (event.key === ' ' || event.key === 'Enter') {
        event.preventDefault();

        const Value = TagInput.value.trim();

        if (Value) {
            const span = document.createElement('span');

            span.className = 'tag';
            span.contentEditable = true;
            span.textContent = Value;

            InteractiveTags.insertBefore(span, TagInput);
            TagInput.value = '';

            manageSpan(span);
        }
    }
});

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
