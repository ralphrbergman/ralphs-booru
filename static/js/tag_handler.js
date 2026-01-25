{
    const InteractiveTags = document.getElementById('interactive-tags');

    function manageSpan(span) {
        function handleSpan() {
            if (span.textContent.trim().length === 0) {
                span.remove();
            }
        }

        span.addEventListener('keyup', function(event) {
            handleSpan();
        });

        span.addEventListener('focusout', function(event) {
            handleSpan();
        });
    }

    // Register event listeners for already existing tag blocks.
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
}

