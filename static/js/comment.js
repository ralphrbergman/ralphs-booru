const CommentForm = document.getElementById('comment-form');

CommentForm.addEventListener('submit', function(event) {
    event.preventDefault();

    const Data = new FormData(event.target);

    fetch('/api/comment', {
        method: 'POST',
        headers: {
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
