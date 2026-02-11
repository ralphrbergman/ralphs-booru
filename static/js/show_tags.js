const interList = document.getElementsByClassName('interactive-tags');
const searchBoxes = document.getElementsByClassName('search-box');

for (let i = 0; i < searchBoxes.length; i++) {
    const searchBox = searchBoxes[i];

    searchBox.classList.remove('hidden');
}

// Show the interactive tag area,
// the legacy input element is automatically hidden.
for (let i = 0; i < interList.length; i++) {
    const interactiveTags = interList[i];

    interactiveTags.classList.remove('hidden');
    interactiveTags.style.display = 'flex';
}
