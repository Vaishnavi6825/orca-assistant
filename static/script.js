
    // =============================
    // Day 12 - UI Revamp JS
    // =============================

    // 🔑 Get or create a session ID for persistent chat memory
    function getSessionId() {
        const urlParams = new URLSearchParams(window.location.search);
        let sessionId = urlParams.get("session_id");

        if (!sessionId) {
            sessionId = crypto.randomUUID();
            urlParams.set("session_id", sessionId);
            window.history.replaceState({}, "", `${location.pathname}?${urlParams}`);
        }
        return sessionId;
    }
    const sessionId = getSessionId();

    document.addEventListener("DOMContentLoaded", () => {
        // 👀 Eye tracking for the Orca
        document.addEventListener("mousemove", (e) => {
            document.querySelectorAll(".eye").forEach((eye) => {
                const rect = eye.getBoundingClientRect();
                const centerX = rect.left + rect.width / 2;
                const centerY = rect.top + rect.height / 2;
                const angle = Math.atan2(e.clientY - centerY, e.clientX - centerX);
                eye.style.transform = `translate(${Math.cos(angle) * 8}px, ${Math.sin(angle) * 8}px)`;
            });
        });

        // 🐳 Orca Assistant click event
        const orcaAvatar = document.getElementById("avatar");
        const responseText = document.getElementById("responseText");
        if (orcaAvatar && responseText) {
            orcaAvatar.addEventListener("click", () => {
                responseText.innerText = "🗨 How can I help you? ";
                responseText.style.display = "block";
                orcaAvatar.style.boxShadow = "0 0 40px #00eaff";
                setTimeout(() => (orcaAvatar.style.boxShadow = "0 0 30px rgba(0, 255, 255, 0.3)"), 1000);
            });
        }
    
        // 🎤 Conversational Agent logic
        let mediaRecorder;
        let audioChunks = [];
        let isRecording = false;

        const recordButton = document.getElementById("recordButton");
        const echoAudio = document.getElementById("echoAudio");
        const statusDiv = document.getElementById("status");
        const chatHistoryDiv = document.getElementById("chatHistory");

        // Append a message bubble to chat history
        function appendChatMessage(role, text) {
            const div = document.createElement("div");
            div.classList.add("chat-message");
            div.classList.add(role === "user" ? "user-msg" : "assistant-msg");
            div.textContent = (role === "user" ? "You: " : "Orca: ") + text;
            chatHistoryDiv.appendChild(div);
            chatHistoryDiv.scrollTop = chatHistoryDiv.scrollHeight;
        }

        // Update chat history UI from full history array
        function updateChatHistory(history) {
            chatHistoryDiv.innerHTML = "";
            history.forEach(msg => {
                appendChatMessage(msg.role, msg.content);
            });
        }

        // Main function to handle recording and API calls
        async function toggleRecording() {
            if (isRecording) {
                // Stop recording
                mediaRecorder.stop();
                isRecording = false;
                recordButton.classList.remove("recording");
                statusDiv.textContent = "🛑 Stopped. Processing...";
                recordButton.disabled = true; // Disable button while processing
            } else {
                // Start recording
                try {
                    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                    mediaRecorder = new MediaRecorder(stream);
                    mediaRecorder.ondataavailable = e => audioChunks.push(e.data);
                    mediaRecorder.onstop = async () => {
                        const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                        audioChunks = [];
                        const formData = new FormData();
                        formData.append("file", audioBlob, "recording.webm");

                        try {
                            statusDiv.textContent = "📤 Sending audio to Orca...";
                            const res = await fetch(`/agent/chat/${sessionId}`, {
                                method: "POST",
                                body: formData
                            });

                            if (!res.ok) {
                                const errorData = await res.json();
                                throw new Error(errorData.detail || "Backend request failed");
                            }

                            const data = await res.json();

                            if (data.error) {
                                console.error("Server-side error:", data.error);
                                statusDiv.textContent = "❌ Interaction failed.";
                                if (data.audio_url) {
                                    echoAudio.src = data.audio_url;
                                    echoAudio.play().catch(e => console.warn("Audio playback blocked.", e));
                                }
                            } else {
                                if (data.chat_history) {
                                    updateChatHistory(data.chat_history);
                                }
                                if (data.audio_url) {
                                    echoAudio.src = data.audio_url;
                                    echoAudio.play().catch(e => console.warn("Audio playback blocked.", e));
                                    echoAudio.onended = () => {
                                        console.log("Bot finished talking, ready for next prompt.");
                                        recordButton.disabled = false; // Re-enable the button
                                        statusDiv.textContent = "Click to speak...";
                                    };
                                } else {
                                    console.warn("No audio URL received.");
                                    recordButton.disabled = false;
                                    statusDiv.textContent = "Click to speak...";
                                }
                                statusDiv.textContent = "✅ Orca replied successfully!";
                            }
                        } catch (err) {
                            console.error("Error:", err);
                            statusDiv.textContent = "❌ Interaction failed.";
                            recordButton.disabled = false; // Re-enable on error
                        }
                    };

                    mediaRecorder.start();
                    isRecording = true;
                    recordButton.classList.add("recording");
                    statusDiv.textContent = "🎤 Recording...";
                } catch (err) {
                    console.error("Microphone access error:", err);
                    statusDiv.textContent = "❌ Microphone access denied.";
                    recordButton.disabled = true;
                }
            }
        }
        
        // Add the click listener to the single button
        recordButton.addEventListener("click", toggleRecording);

    });
