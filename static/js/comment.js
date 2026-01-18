const ApiKey = document.getElementById('api-key').textContent;
const CommentForm = document.getElementById('comment-form');
const ContentArea = document.querySelector('textarea[name="content"]');

CommentForm.addEventListener('submit', function(event) {
    event.preventDefault();

    const Data = new FormData(event.target);
    const Content = Data.get('content').trim();
    if (Content.length === 0) {
        return;
    }

    fetch('/api/comment', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${ApiKey}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            'content': Content,
            'post_id': Data.get('post_id')
        })
    }).then((Response) => {
        if (Response.ok) {
            ContentArea.value = '';
            return Response.json();
        }
    }).then((Json) => {
        if (Json['created']) {
            location.reload();
        }
    });
});
