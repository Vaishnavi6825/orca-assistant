// =============================
// Day 9 - Orca AI Assistant JS
// =============================

// Ensure the code is wrapped in a DOMContentLoaded listener
// to prevent errors if the script loads before the HTML elements.
document.addEventListener("DOMContentLoaded", () => {
  // 👀 Eye tracking for the Orca
  // This logic is adapted for the `::after` pseudo-element used as the pupil.
  document.addEventListener("mousemove", (e) => {
    document.querySelectorAll(".eye").forEach((eye) => {
      const rect = eye.getBoundingClientRect();
      const centerX = rect.left + rect.width / 2;
      const centerY = rect.top + rect.height / 2;
      const angle = Math.atan2(e.clientY - centerY, e.clientX - centerX);
      // The CSS transforms the pseudo-element relative to the parent.
      // We apply the transform to the parent `.eye` element.
      eye.style.transform = `translate(${Math.cos(angle) * 8}px, ${Math.sin(angle) * 8}px)`;
    });
  });

  // 🐳 Orca Assistant click event
  // The HTML already has an onclick attribute, but this listener provides a more
  // robust way to handle the click event and visual feedback.
  const orcaAvatar = document.getElementById("avatar");
  const responseText = document.getElementById("responseText");
  orcaAvatar.addEventListener("click", () => {
    responseText.innerText = "🗨 How can I help you? ";
    responseText.style.display = "block";

    orcaAvatar.style.boxShadow = "0 0 40px #00eaff";
    setTimeout(() => (orcaAvatar.style.boxShadow = "0 0 30px rgba(0, 255, 255, 0.3)"), 1000);
  });

  // 🔊 Text-to-Speech (manual input)
  // This function is called from the 'Speak' button's onclick attribute.
  async function sendText() {
    const text = document.getElementById("ttsInput").value;
    if (!text) return;

    try {
      const payload = {
        text: text,
        voiceId: "en-US-natalie" // This matches the voiceId in your backend
      };

      const response = await fetch("/api/tts", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      if (!response.ok) throw new Error("TTS API request failed.");
      const data = await response.json();
      const audioPlayer = document.getElementById("ttsAudio");

      if (!data.audioFile) throw new Error("No audio file returned from Murf.");
      audioPlayer.src = data.audioFile;
      audioPlayer.style.display = "block";
      await audioPlayer.play().catch(e => {
        console.warn("Audio playback was blocked. User interaction required.", e);
      });
    } catch (err) {
      console.error("TTS Error:", err);
      // Use a custom message box instead of alert()
      // You can add a div for this and style it
      const errorMessage = document.createElement('div');
      errorMessage.textContent = "Failed to generate audio. Check the console for details.";
      errorMessage.style.cssText = "position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%); background: #ff0000; color: white; padding: 10px 20px; border-radius: 5px; z-index: 9999;";
      document.body.appendChild(errorMessage);
      setTimeout(() => errorMessage.remove(), 5000);
    }
  }
  // Expose sendText to the global scope so the HTML `onclick` can find it.
  window.sendText = sendText;

  // 🎤 Echo Bot v2 functionality (Audio -> Whisper -> LLM -> Murf TTS)
  let mediaRecorder;
  let audioChunks = [];

  const startBtn = document.getElementById("startRecording");
  const stopBtn = document.getElementById("stopRecording");
  const echoAudio = document.getElementById("echoAudio");
  const status = document.getElementById("uploadStatus");
  const transcriptBox = document.getElementById("transcriptText");

  // Get microphone access and set up the MediaRecorder
  navigator.mediaDevices.getUserMedia({ audio: true })
    .then(stream => {
      mediaRecorder = new MediaRecorder(stream);

      mediaRecorder.ondataavailable = e => {
        audioChunks.push(e.data);
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
        audioChunks = [];

        const formData = new FormData();
        formData.append("file", audioBlob, "recording.webm");

        try {
          status.textContent = "📤 Sending audio to Orca ...";
          transcriptBox.textContent = ""; // Clear previous transcript
          echoAudio.style.display = "none"; // Hide previous audio player

          // Call the `/llm/query/audio` endpoint from your main.py
          const res = await fetch("/llm/query/audio", {
            method: "POST",
            body: formData
          });

          if (!res.ok) throw new Error(`Backend request failed with status: ${res.status}`);
          const data = await res.json();

          // Display the transcript and LLM response
          transcriptBox.innerHTML = `
            ✍ Transcription: ${data.transcript || "No text detected"}<br>
            🤖 LLM Response: ${data.llm_response || "No response"}
          `;

          // Play the Murf audio reply
          if (data.audio_url) {
            echoAudio.src = data.audio_url;
            echoAudio.style.display = "block";
            await echoAudio.play().catch(e => {
              console.warn("Audio playback was blocked. User interaction required.", e);
            });
          }

          status.textContent = "✅ Orca replied successfully!";
        } catch (err) {
          console.error("Error:", err);
          status.textContent = "❌ Day 9 interaction failed.";
          transcriptBox.textContent = "Error: See console for details.";
        }
      };

      // Event listeners for the record buttons
      startBtn.onclick = () => {
        audioChunks = [];
        mediaRecorder.start();
        startBtn.disabled = true;
        stopBtn.disabled = false;
        status.textContent = "🎤 Recording...";
      };

      stopBtn.onclick = () => {
        mediaRecorder.stop();
        startBtn.disabled = false;
        stopBtn.disabled = true;
        status.textContent = "🛑 Stopped. Processing...";
      };
    })
    .catch(err => {
      console.error("Microphone access error:", err);
      // Use a custom message box instead of alert()
      const errorMessage = document.createElement('div');
      errorMessage.textContent = "Microphone access is required to use the Echo Bot.";
      errorMessage.style.cssText = "position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%); background: #ff0000; color: white; padding: 10px 20px; border-radius: 5px; z-index: 9999;";
      document.body.appendChild(errorMessage);
      setTimeout(() => errorMessage.remove(), 5000);
    });
});
