{
    const interactiveTags = document.getElementById('interactive-tags');

    function getSpans() {
        return document.querySelectorAll('span.tag');
    }

    function getSpanByContent(element) {
        const spanTags = getSpans();

        for (let i = 0; i < spanTags.length; i++) {
            let span = spanTags[i];

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
    const spanTags = getSpans();

    spanTags.forEach(function(span) {
        manageSpan(span);
    });

    // Handle creating new tags.
    const tagInput = interactiveTags.querySelector('input.tag');

    tagInput.addEventListener('keydown', function(event) {
        if (event.key === ' ' || event.key === 'Enter') {
            event.preventDefault();

            const Value = tagInput.value.trim();

            if (Value && !getSpanByContent(tagInput)) {
                const span = document.createElement('span');

                span.className = 'tag';
                span.contentEditable = true;
                span.textContent = Value;

                interactiveTags.insertBefore(span, tagInput);
                tagInput.value = '';

                manageSpan(span);
            }
        }
    });
}

