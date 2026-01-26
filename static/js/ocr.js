const DetectBtn = document.getElementById('ocr-btn');
const Caption = document.querySelector('[name="caption"]');

DetectBtn.addEventListener('click', async function() {
    const Image = document.querySelector('.view-container img');
    // Tesseract detection.
    const Worker = await Tesseract.createWorker('eng');
    const { data: { text } } = await Worker.recognize(Image);

    Caption.textContent = text;
    window.resizeTextArea(Caption);
});
