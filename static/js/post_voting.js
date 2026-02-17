/**
 * JavaScript module providing the ability to vote posts.
*/
import { vote } from './voting.js';

const postId = parseInt(document.getElementById('post-id').textContent);
const upvoteBtn = document.getElementById('upvote-btn');
const downvoteBtn = document.getElementById('downvote-btn');

upvoteBtn.addEventListener('click', function(event) {
    vote(event, postId, 1, 'post')
});

downvoteBtn.addEventListener('click', function(event) {
    vote(event, postId, -1, 'post')
});
