function vote(event, postId, score) {
    event.preventDefault();

    const Url = `/api/score?post_id=${postId}`
    let method;

    if (score == 1) {
        method = 'POST';
    } else {
        method = 'DELETE';
    }

    fetch(Url, {
        method: method,
        headers: {
            'Content-Type': 'application/json'
        }
    }).then(response => {
        if (response.ok) {
            location.reload();
        }
    })
}
