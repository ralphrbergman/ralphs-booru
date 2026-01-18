const ApiKey = document.getElementById('api-key').textContent;
const CommentForm = document.getElementById('comment-form');

CommentForm.addEventListener('submit', function(event) {
    event.preventDefault();

    const Data = new FormData(event.target);
    if (Data.get('content').length === 0) {
        return;
    }

    fetch('/api/comment', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${ApiKey}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            'content': Data.get('content'),
            'post_id': Data.get('post_id')
        })
    }).then((Response) => {
        if (Response.ok) {
            location.reload();
        }
    });
});
