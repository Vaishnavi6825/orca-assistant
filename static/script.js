// Eye tracking
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

// Pulsing glow effect
setInterval(() => {
  const avatar = document.getElementById("avatar");
  avatar.style.opacity = 0.7;
  setTimeout(() => avatar.style.opacity = 1, 200);
}, 5000);

// Show message on click
document.getElementById("avatar").addEventListener("click", () => {
  const response = document.getElementById("responseText");
  response.innerText = "🐳 I'm your Orca Assistant!";
  response.style.display = "block";

  // Optional: temporary glow
  const avatar = document.getElementById("avatar");
  avatar.style.boxShadow = "0 0 40px #00eaff";
  setTimeout(() => avatar.style.boxShadow = "0 0 30px #00bfff55", 1000);
});
