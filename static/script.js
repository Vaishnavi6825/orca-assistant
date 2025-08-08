// 🎯 Eye tracking
document.addEventListener("mousemove", (e) => {
  document.querySelectorAll(".eye").forEach((eye) => {
    const pupil = eye.querySelector(".pupil");
    const rect = eye.getBoundingClientRect();
    const centerX = rect.left + rect.width / 2;
    const centerY = rect.top + rect.height / 2;
    const angle = Math.atan2(e.clientY - centerY, e.clientX - centerX);
    pupil.style.transform = `translate(${Math.cos(angle) * 4}px, ${Math.sin(angle) * 4}px)`;
  });
});

// ✨ Avatar glow
setInterval(() => {
  const avatar = document.getElementById("avatar");
  avatar.style.opacity = 0.7;
  setTimeout(() => (avatar.style.opacity = 1), 200);
}, 5000);

// 🐳 Orca Assistant click
document.getElementById("avatar").addEventListener("click", () => {
  const response = document.getElementById("responseText");
  response.innerText = "🐳 I'm your Orca Assistant!";
  response.style.display = "block";

  const avatar = document.getElementById("avatar");
  avatar.style.boxShadow = "0 0 40px #00eaff";
  setTimeout(() => (avatar.style.boxShadow = "0 0 30px #00bfff55"), 1000);
});

// 🔊 Text-to-Speech (manual input → Murf)
async function sendText() {
  const text = document.getElementById("ttsInput").value;
  if (!text) return;

  try {
    const response = await fetch("/api/tts", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text, voiceId: "en-US-natalie" })
    });

    const data = await response.json();
    const audioPlayer = document.getElementById("ttsAudio");

    if (!data.audioFile) throw new Error("No audio file returned");
    audioPlayer.src = data.audioFile;
    audioPlayer.style.display = "block";
    await audioPlayer.play();
  } catch (err) {
    console.error("TTS Error:", err);
    alert("Failed to generate audio.");
  }
}

// 📤 Upload + Murf Echo + Transcribe
async function uploadAudio(blob) {
  const status = document.getElementById("uploadStatus");
  const transcriptBox = document.getElementById("transcriptText");
  transcriptBox.style.display = "none";

  const formData = new FormData();
  formData.append("file", blob, "recording.webm");

  try {
    // Step 1: Send to /tts/echo for Murf's voice
    status.textContent = "📤 Sending to Murf for echo...";
    const echoRes = await fetch("/tts/echo", {
      method: "POST",
      body: formData
    });

    if (!echoRes.ok) throw new Error("Echo TTS failed");
    const echoData = await echoRes.json();
    if (!echoData.audio_url) throw new Error("No audio_url from Murf");

    const echoAudio = document.getElementById("echoAudio");
    echoAudio.src = echoData.audio_url;
    echoAudio.style.display = "block";
    await echoAudio.play();

    // Step 2: Upload for transcription
    status.textContent = "🧠 Transcribing...";
    const transcribeRes = await fetch("/transcribe/file", {
      method: "POST",
      body: formData
    });

    if (!transcribeRes.ok) throw new Error("Transcription failed");
    const transcribeData = await transcribeRes.json();

    transcriptBox.textContent = `✍ Transcription: ${transcribeData.text || "No text found"}`;
    transcriptBox.style.display = "block";
    status.textContent = "✅ Done!";
  } 
  catch (err) 
  {
    console.error("❌ Error:", err);
    status.textContent = "❌ Murf echo or transcription failed.";
  }
}

// 🎙️ Audio recording logic
let mediaRecorder;
let audioChunks = [];

const startBtn = document.getElementById("startRecording");
const stopBtn = document.getElementById("stopRecording");
const echoAudio = document.getElementById("echoAudio");
const status = document.getElementById("uploadStatus");

startBtn.addEventListener("click", async () => {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream);
    audioChunks = [];

    mediaRecorder.ondataavailable = (e) => {
      audioChunks.push(e.data);
    };

    mediaRecorder.onstop = async () => {
      const blob = new Blob(audioChunks, { type: "audio/webm" });
      await uploadAudio(blob);
    };

    mediaRecorder.start();
    startBtn.disabled = true;
    stopBtn.disabled = false;
    status.textContent = "🎙️ Recording...";
  } catch (err) {
    console.error("Microphone error:", err);
    alert("Microphone access is required.");
  }
});

stopBtn.addEventListener("click", () => {
  if (mediaRecorder && mediaRecorder.state !== "inactive") {
    mediaRecorder.stop();
    startBtn.disabled = false;
    stopBtn.disabled = true;
    status.textContent = "🛑 Stopped. Processing...";
  }
});
