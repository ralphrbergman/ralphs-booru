const interList = document.getElementsByClassName('interactive-tags');

export function createTag(tagName, interactiveTags, tagInput) {
    /**
     * Adds new tag to interactive tag area.
     * @param {string} tagName Tag to add.
     * @param {HTMLDivElement} interactiveTags Specific interactive tags element.
     * @param {HTMLInputElement} tagInput Input element, used to position tag before it.
    */
    const span = document.createElement('span');

    span.className = 'tag';
    span.contentEditable = true;
    span.textContent = tagName;

    interactiveTags.insertBefore(span, tagInput.parentElement);
    tagInput.value = '';

    manageSpan(span, interactiveTags);
}

export function getSpans(interactiveTags) {
    /**
     * Obtains tags from interactive tag area.
     * @param {HTMLDivElement} interactiveTags Specific tag area.
     * @returns {NodeList<HTMLSpanElement>}
    */
    return interactiveTags.querySelectorAll('span.tag');
}

export function getSpanByContent(element, interactiveTags) {
    /**
     * Obtain specific element by tag name from another span element.
     * @param {HTMLSpanElement} element Span element to compare.
     * @param {HTMLDivElement} interactiveTags Tag area to select from.
     * @returns {HTMLSpanElement} The span whose value matches.
    */
    const spanTags = getSpans(interactiveTags);

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

export function getTags(interactiveTags) {
    /**
     * Obtains tag names from tag area.
     * @param {HTMLDivElement} interactiveTags Specific tag area
     * @returns {string[]}
    */
    const tags = [];

    getSpans(interactiveTags).forEach(function(span) {
        tags.push(span.textContent);
    });

    const tagInInput = interactiveTags.querySelector('input.tag').value.trim();

    // Also include the not committed tag in input field.
    if (tagInInput) tags.push(tagInInput);

    return tags;
}

export function manageSpan(span, interactiveTags) {
    /**
     * Handles span for tagging.
     * @param {HTMLSpanElement} span Span who should be handled.
     * @param {HTMLDivElement} interactiveTags Specific tag area.
    */
    function handleSpan() {
        if (span.textContent.trim().length === 0) {
            span.remove();
        }
    }

    span.addEventListener('keydown', function(event) {
        if (event.key === 'Enter' || event.key === ' ') {
            event.preventDefault();

            if (!getSpanByContent(span, interactiveTags)) {
                span.nextSibling.focus();
            }
        }
    });

    span.addEventListener('focusout', function(event) {
        if (getSpanByContent(span, interactiveTags)) {
            span.remove();
            return;
        }

        handleSpan();
    });
}

for (let i = 0; i < interList.length; i++) {
    const interactiveTags = interList[i];
    const tagInput = interactiveTags.querySelector('input.tag');

    // Register event listeners for already existing tag blocks.
    const spanTags = getSpans(interactiveTags);

    spanTags.forEach(function(span) {
        manageSpan(span, interactiveTags);
    });

    // Handle creating new tags.
    tagInput.addEventListener('keydown', function(event) {
        if (event.key === ' ' || event.key === 'Enter') {
            event.preventDefault();

            const Value = tagInput.value.trim();

            if (Value && !getSpanByContent(tagInput, interactiveTags)) {
                createTag(Value, interactiveTags, tagInput);
            }
        }
    });
}
