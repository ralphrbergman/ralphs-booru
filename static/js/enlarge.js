const enlargeBtn = document.getElementById('enlarge-btn');
const btnText = enlargeBtn.textContent;

const element = document.querySelector(
    '.view-container audio, .view-container img, .view-container video'
);

// Makes the element show within bounds of a small screen.
const mobileQuery = window.matchMedia('(max-width: 768px)');

mobileQuery.addEventListener('change', function(event) {
    if (event.matches) {
        element.style.width = '100vw';
    }
});

// Handle minimizing/maximizing element.
enlargeBtn.addEventListener('click', function() {
    if (element.style.height === '' || element.style.height === '100vh') {
        element.style.height = 'auto';
        element.style.width = 'auto';
        enlargeBtn.textContent = 'Minimize';
    } else {
        element.style.height = '100vh';
        element.style.width = '100vw';
        enlargeBtn.textContent = btnText;
    }
});
