function vote(event, targetId, score, targetType = 'post') {
    event.preventDefault();

    const Url = `/api/score?target_id=${targetId}&target_type=${targetType}`
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
