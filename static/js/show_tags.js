const InteractiveTags = document.getElementById('interactive-tags');

// Show the interactive tag area, the other one is automatically hidden.
if (InteractiveTags) {
    InteractiveTags.classList.remove('hidden');
    InteractiveTags.style.display = 'flex';
}
