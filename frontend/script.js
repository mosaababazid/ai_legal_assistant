// script.js - Minimal, dependency-free frontend for file upload and displaying results.
const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file');
const form = document.getElementById('uploadForm');
const resultDiv = document.getElementById('result');
const originalText = document.getElementById('original_text');
const summaryText = document.getElementById('summary');
const legalAdvice = document.getElementById('legal_recommendation');
const usedParagraphsList = document.getElementById('used_paragraphs');
const progress = document.getElementById('progress');
const progressBar = document.getElementById('progress-bar');
const loadingDiv = document.getElementById('loading');

const API_URL = 'http://127.0.0.1:8000/api/extract-summarize';

function setDropZoneText(text) {
    dropZone.textContent = text;
}

function setProgress(percent) {
    progress.style.display = 'block';
    progressBar.style.width = `${percent}%`;
    progressBar.textContent = `${percent}%`;
}

function resetProgress() {
    progress.style.display = 'none';
    progressBar.style.width = '0%';
    progressBar.textContent = '0%';
}

function renderUsedParagraphs(paragraphs) {
    usedParagraphsList.innerHTML = '';

    if (!Array.isArray(paragraphs) || paragraphs.length === 0) {
        const li = document.createElement('li');
        li.textContent = 'Keine Paragraphen erkannt oder im Index enthalten.';
        usedParagraphsList.appendChild(li);
        return;
    }

    paragraphs.forEach((paragraph) => {
        const li = document.createElement('li');
        li.textContent = paragraph;
        usedParagraphsList.appendChild(li);
    });
}

function setSelectedFile(file) {
    if (!file) {
        setDropZoneText('Datei hierher ziehen oder klicken');
        return;
    }

    setDropZoneText(`Ausgewählt: ${file.name}`);
}

['dragenter', 'dragover'].forEach((eventName) => {
    dropZone.addEventListener(eventName, (event) => {
        event.preventDefault();
        dropZone.classList.add('dragover');
        setDropZoneText('Datei ablegen');
    });
});

['dragleave', 'drop'].forEach((eventName) => {
    dropZone.addEventListener(eventName, (event) => {
        event.preventDefault();
        dropZone.classList.remove('dragover');
        setSelectedFile(fileInput.files?.[0]);
    });
});

dropZone.addEventListener('click', () => fileInput.click());
dropZone.addEventListener('keydown', (event) => {
    if (event.key === 'Enter' || event.key === ' ') fileInput.click();
});

dropZone.addEventListener('drop', (event) => {
    const files = event.dataTransfer?.files;
    if (!files || files.length === 0) return;

    fileInput.files = files;
    setSelectedFile(files[0]);
});

fileInput.addEventListener('change', () => {
    setSelectedFile(fileInput.files?.[0]);
});

form.addEventListener('submit', async (event) => {
    event.preventDefault();
    if (!fileInput.files || fileInput.files.length === 0) {
        alert('Bitte eine Datei auswählen.');
        return;
    }

    const formData = new FormData(form);
    const xhr = new XMLHttpRequest();

    resultDiv.style.display = 'none';
    loadingDiv.style.display = 'block';
    resetProgress();

    xhr.open('POST', API_URL);

    xhr.upload.addEventListener('progress', (e) => {
        if (!e.lengthComputable) return;
        const percent = Math.round((e.loaded / e.total) * 100);
        setProgress(percent);
    });

    xhr.onload = () => {
        loadingDiv.style.display = 'none';
        resetProgress();

        if (xhr.status < 200 || xhr.status >= 300) {
            console.error('Request failed', xhr.status, xhr.responseText);
            alert(`Serverfehler (HTTP ${xhr.status}).`);
            return;
        }

        try {
            const data = JSON.parse(xhr.responseText);
            originalText.textContent = data.original_text || 'Kein Text extrahiert.';
            summaryText.textContent = data.summary || 'Keine Zusammenfassung vorhanden.';
            legalAdvice.textContent = data.legal_recommendation || '';
            renderUsedParagraphs(data.used_paragraphs);
            resultDiv.style.display = 'block';
        } catch (error) {
            console.error('Failed to parse JSON response', error);
            alert('Antwort konnte nicht gelesen werden.');
        }
    };

    xhr.onerror = () => {
        loadingDiv.style.display = 'none';
        resetProgress();
        console.error('Network error');
        alert('Anfrage fehlgeschlagen.');
    };

    xhr.send(formData);
});

// Optional: minimal dark mode toggle.
const toggle = document.createElement('button');
toggle.type = 'button';
toggle.textContent = 'Dark mode';
toggle.className = 'dark-mode-toggle';
toggle.addEventListener('click', () => {
    document.body.classList.toggle('dark-mode');
    toggle.classList.toggle('active');
});
document.body.appendChild(toggle);

