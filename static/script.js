// 👁️ Eye tracking
document.addEventListener("mousemove", (e) => {
  const eyes = document.querySelectorAll(".eye");
  eyes.forEach((eye) => {
    const pupil = eye.querySelector(".pupil");
    const rect = eye.getBoundingClientRect();
    const centerX = rect.left + rect.width / 2;
    const centerY = rect.top + rect.height / 2;
    const angle = Math.atan2(e.clientY - centerY, e.clientX - centerX);
    const dx = Math.cos(angle) * 4;
    const dy = Math.sin(angle) * 4;
    pupil.style.transform = `translate(${dx}px, ${dy}px)`;
  });
});

// ✨ Pulsing glow effect
setInterval(() => {
  const avatar = document.getElementById("avatar");
  avatar.style.opacity = 0.7;
  setTimeout(() => {
    avatar.style.opacity = 1;
  }, 200);
}, 5000);

// 🐳 Orca click message
document.getElementById("avatar").addEventListener("click", () => {
  const response = document.getElementById("responseText");
  response.innerText = "🐳 I'm your Orca Assistant!";
  response.style.display = "block";

  const avatar = document.getElementById("avatar");
  avatar.style.boxShadow = "0 0 40px #00eaff";
  setTimeout(() => {
    avatar.style.boxShadow = "0 0 30px #00bfff55";
  }, 1000);
});

// 🔊 TTS integration (Murf)
async function generateAudio() {
  const text = document.getElementById("textInput").value;
  if (!text) {
    alert("Please enter some text.");
    return;
  }

  try {
    const response = await fetch("/api/tts", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ text: text, voiceId: "en-US-natalie" })
    });

    if (!response.ok) throw new Error("API Error");

    const data = await response.json();
    const audioUrl = data.audioFile;  // ✅ this matches your backend

    if (!audioUrl) throw new Error("No audio URL in response");

    const player = document.getElementById("audioPlayer");
    player.src = audioUrl;
    player.load(); // ensures browser reloads audio
    player.style.display = "block";
    await player.play().catch(() => {
      console.warn("Autoplay blocked. User may need to click play.");
    });

  } catch (error) {
    console.error("❌ Error:", error);
    alert("Failed to generate audio.");
  }
}
