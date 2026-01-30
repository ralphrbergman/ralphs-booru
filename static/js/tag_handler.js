{
    const InteractiveTags = document.getElementById('interactive-tags');

    function getSpans() {
        return document.querySelectorAll('span.tag');
    }

    function getSpanByContent(element) {
        const SpanTags = getSpans();

        for (let i = 0; i < SpanTags.length; i++) {
            let span = SpanTags[i];

            if (element.tagName === 'SPAN') {
                if (span.textContent == element.textContent && span !== element) {
                    return span;
                }
            } else {
                if (span.textContent == element.value && span !== element) {
                    return span;
                }
            }
        }
    }

    function manageSpan(span) {
        function handleSpan() {
            if (span.textContent.trim().length === 0) {
                span.remove();
            }
        }

        span.addEventListener('keydown', function(event) {
            if (event.key === 'Enter' || event.key === ' ') {
                event.preventDefault();

                if (!getSpanByContent(span)) {
                    span.nextSibling.focus();
                }
            }
        });

        span.addEventListener('focusout', function(event) {
            if (getSpanByContent(span)) {
                span.remove();
                return;
            }

            handleSpan();
        });
    }

    // Register event listeners for already existing tag blocks.
    const SpanTags = getSpans();

    SpanTags.forEach(function(span) {
        manageSpan(span);
    });

    // Handle creating new tags.
    const TagInput = InteractiveTags.querySelector('input.tag');

    TagInput.addEventListener('keydown', function(event) {
        if (event.key === ' ' || event.key === 'Enter') {
            event.preventDefault();

            const Value = TagInput.value.trim();

            if (Value && !getSpanByContent(TagInput)) {
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

