/**
 * JavaScript module providing the capability of publishing comments.
*/
const apiKey = document.getElementById('api-key').textContent;
const commentForm = document.getElementById('comment-form');
const contentArea = document.querySelector('textarea[name="content"]');

// Handle form submission.
commentForm.addEventListener('submit', function(event) {
    event.preventDefault();

    const data = new FormData(event.target);

    const content = data.get('content').trim();
    if (content.length === 0) {
        return;
    }

    // Send the request.
    fetch('/api/comment', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${apiKey}`,
            'content-Type': 'application/json'
        },
        body: JSON.stringify({
            'content': content,
            'post_id': data.get('post_id')
        })
    }).then((response) => {
        contentArea.value = '';

        if (response.ok) {
            return response.json();
        }
    }).then((Json) => {
        if (Json && Json['created']) {
            location.reload();
        }
    });
});
