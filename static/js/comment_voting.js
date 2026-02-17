/**
 * JavaScript module providing the ability to vote on comments.
*/
import { vote } from './voting.js';

const upBtns = document.getElementsByClassName('com-upvote-btn');
const downBtns = document.getElementsByClassName('com-downvote-btn');
const buttons = [ ...upBtns, ...downBtns ];

for (let i = 0; i < buttons.length; i++) {
    const btn = buttons[i];
    const commentId = parseInt(btn.closest('.comment').dataset.commentId);

    const value = btn.classList.contains('com-upvote-btn') ? 1 : -1;

    btn.addEventListener('click', function(event) {
        vote(event, commentId, value, 'comment');
    });
}
