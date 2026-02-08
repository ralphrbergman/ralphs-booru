const interactiveTags = document.getElementById('interactive-tags');

// Show the interactive tag area, the other one is automatically hidden.
if (interactiveTags) {
    interactiveTags.classList.remove('hidden');
    interactiveTags.style.display = 'flex';
}
