function vote(event, targetId, score, targetType = 'post') {
    event.preventDefault();

    fetch(`/api/score`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            'target_id': targetId,
            'target_type': targetType,
            'value': score
        })
    }).then(response => {
        if (response.ok) {
            location.reload();
        }
    })
}
