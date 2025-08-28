// Set sample text based on language
function setSampleText(lang, text) {
    document.getElementById('textInput').value = text;
    document.getElementById('languageSelect').value = lang;
}

async function generateAudio() {
    const text = document.getElementById('textInput').value.trim();
    const language = document.getElementById('languageSelect').value;
    const status = document.getElementById('status');
    const audioPlayer = document.getElementById('audioPlayer');

    status.className = 'info';
    status.textContent = '';

    if (!text) {
        status.className = 'error';
        status.textContent = "Please enter some text";
        return;
    }

    status.className = '';
    status.textContent = "Generating speech...";

    try {
        const response = await fetch('/generate-speech', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text, language })
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.error || `Server error: ${response.status}`);
        }

        const audioBlob = await response.blob();
        const audioUrl = URL.createObjectURL(audioBlob);

        // Clean up previous audio object URLs
        if (audioPlayer.src) {
            URL.revokeObjectURL(audioPlayer.src);
        }

        audioPlayer.src = audioUrl;
        status.className = 'success';
        status.textContent = "Speech generated successfully!";
    } catch (error) {
        status.className = 'error';
        status.textContent = "Error: " + error.message;
        console.error("TTS generation failed:", error);
    }
}

// Check health on load
window.addEventListener('load', async () => {
    try {
        const response = await fetch('/health');
        if (response.ok) {
            const data = await response.json();
            console.log("Service details:", data);

            // Verify we're using the correct buffer implementation
            if (data.buffer_implementation !== 'wave_file_interface') {
                document.getElementById('status').className = 'error';
                document.getElementById('status').textContent =
                    "BUFFER MISMATCH: Expected wave file interface implementation";
            }
        } else {
            throw new Error("Health check failed");
        }
    } catch (e) {
        document.getElementById('status').className = 'error';
        document.getElementById('status').textContent = "Service not available - check console";
        console.error("Health check failed:", e);
    }
});
