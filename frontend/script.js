// Set sample text based on language
function setSampleText(lang, text) {
    document.getElementById('textInput').value = text;
    document.getElementById('languageSelect').value = lang;
}

async function generateAudio() {
    const text = document.getElementById('textInput').value.trim();
    const language = document.getElementById('languageSelect').value;
    const speaker = document.getElementById('speakerSelect').value;
    const status = document.getElementById('status');
    const audioPlayer = document.getElementById('audioPlayer');

    // Get current language for translations
    const currentLang = localStorage.getItem('selectedLanguage') || 'tr';
    const t = window.translations[currentLang];

    status.className = 'info';
    status.textContent = '';

    if (!text) {
        status.className = 'error';
        status.textContent = t.errorNoText;
        return;
    }

    status.className = '';
    status.textContent = t.generating;

    try {
        const response = await fetch('/generate-speech', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text, language, speaker })
        });

        if (!response.ok) {
            // Handle rate limiting specifically
            if (response.status === 429) {
                throw new Error(t.errorRateLimited);
            }
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.error || 'Server error:' + response.status);
        }

        const audioBlob = await response.blob();
        const audioUrl = URL.createObjectURL(audioBlob);

        // Clean up previous audio object URLs
        if (audioPlayer.src) {
            URL.revokeObjectURL(audioPlayer.src);
        }

        audioPlayer.src = audioUrl;
        status.className = 'success';
        status.textContent = t.successGenerated;
    } catch (error) {
        status.className = 'error';
        status.textContent = t.errorPrefix + error.message;
        console.error(t.consoleTTSFailed, error);
    }
}

// Check health on load
window.addEventListener('load', async () => {
    try {
        const response = await fetch('/health');
        if (response.ok) {
            const data = await response.json();
            const currentLang = localStorage.getItem('selectedLanguage') || 'tr';
            const t = window.translations[currentLang];
            console.log(t.consoleServiceDetails, data);

            // Verify we're using the correct buffer implementation
            if (data.buffer_implementation !== 'wave_file_interface') {
                document.getElementById('status').className = 'error';
                document.getElementById('status').textContent = t.errorBufferMismatch;
            }
        } else {
            throw new Error("Health check failed");
        }
    } catch (e) {
        const currentLang = localStorage.getItem('selectedLanguage') || 'tr';
        const t = window.translations[currentLang];
        document.getElementById('status').className = 'error';
        document.getElementById('status').textContent = t.errorServiceNotAvailable;
        console.error(t.consoleHealthCheckFailed, e);
    }
});
