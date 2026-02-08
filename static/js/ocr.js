const detectBtn = document.getElementById('ocr-btn');
const caption = document.querySelector('[name="caption"]');

detectBtn.addEventListener('click', async function() {
    const image = document.querySelector('.view-container img');
    // Tesseract detection.
    const worker = await Tesseract.createWorker('eng');
    const { data: { text } } = await worker.recognize(image);

    caption.textContent = text;
    window.resizeTextArea(caption);
});
