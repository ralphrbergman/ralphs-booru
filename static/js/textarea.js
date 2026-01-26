// JavaScript for automatically resizing TextAreas according to their content.

window.resizeTextArea = function(textArea) {
    textArea.style.height = 'auto';
    textArea.style.height = textArea.scrollHeight + 'px';
    textArea.style.height = textArea.scrollHeight + 'px';
}

document.querySelectorAll('textarea').forEach(function(textArea) {
    window.resizeTextArea(textArea);

    textArea.addEventListener('input', function() {
        window.resizeTextArea(textArea);
    });
});
