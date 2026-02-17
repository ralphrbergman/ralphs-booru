/**
 * JavaScript module that provides the API of voting posts/comments.
*/
import { sendErrorMessage } from "./message.js";

const apiKey = document.getElementById('api-key').textContent;

export function vote(event, targetId, score, targetType = 'post') {
    /**
     * Marks a vote for specific target.
     * @param {MouseEvent} event Event to stop midway from submitting.
     * @param {number} targetId
     * @param {number} score -1 for negative voting and 1 for positive. 
     * @param {string} targetType
    */
    event.preventDefault();

    fetch(`/api/score`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${apiKey}`,
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

            sendErrorMessage(`Error: ${json['message']}`);
        }
    })
}
