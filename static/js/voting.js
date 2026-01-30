import { sendErrorMessage } from "./message.js";

const postId = document.getElementById('post-id').textContent;
const upvoteBtn = document.getElementById('upvote-btn');
const downvoteBtn = document.getElementById('downvote-btn');

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
    }).then(async function (response) {
        if (response.ok) {
            location.reload();
        } else {
            const json = await response.json();

            sendErrorMessage(`Error: ${json['detail']}`);
        }
    })
}

upvoteBtn.addEventListener('click', function(event) {
    vote(event, parseInt(postId), 1, 'post')
});

downvoteBtn.addEventListener('click', function(event) {
    vote(event, parseInt(postId), -1, 'post')
});
