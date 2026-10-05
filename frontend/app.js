const chat = document.getElementById("chat");
const form = document.getElementById("chatForm");
const messageInput = document.getElementById("message");
const sendBtn = document.getElementById("sendBtn");
const mode = document.getElementById("mode");
const difficulty = document.getElementById("difficulty");
const clearBtn = document.getElementById("clearBtn");
const statusBadge = document.getElementById("statusBadge");

let history = [];

function addMessage(role, text) {
  const wrapper = document.createElement("div");
  wrapper.className = `message ${role}`;

  const avatar = document.createElement("div");
  avatar.className = "avatar";
  avatar.textContent = role === "user" ? "YOU" : "AI";

  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.textContent = text;

  wrapper.appendChild(avatar);
  wrapper.appendChild(bubble);
  chat.appendChild(wrapper);
  chat.scrollTop = chat.scrollHeight;

  return wrapper;
}

function setStatus(text, good = true) {
  statusBadge.textContent = text;
  statusBadge.style.color = good ? "#18794e" : "#b42318";
}

async function checkHealth() {
  try {
    const res = await fetch("/api/health");
    const data = await res.json();

    if (data.llm_configured) {
      const providerText = data.provider === "local" ? "Local Gemma" : "OpenAI";
      setStatus(`${providerText} ready · ${data.model}`, true);
    } else {
      setStatus("Configure the selected LLM in .env", false);
    }
  } catch {
    setStatus("Backend not reachable", false);
  }
}

async function sendMessage(text) {
  const clean = text.trim();
  if (!clean) return;

  addMessage("user", clean);
  history.push({ role: "user", content: clean });
  messageInput.value = "";

  sendBtn.disabled = true;
  sendBtn.textContent = "Teaching…";

  const loading = addMessage("assistant", "Thinking through the concept…");
  loading.classList.add("loading");

  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        message: clean,
        history,
        mode: mode.value,
        difficulty: difficulty.value
      })
    });

    const data = await response.json();

    loading.remove();

    if (!response.ok) {
      throw new Error(data.detail || "The backend returned an error.");
    }

    addMessage("assistant", data.answer);
    history.push({ role: "assistant", content: data.answer });
  } catch (error) {
    addMessage(
      "assistant",
      `I could not complete that request.\n\n${error.message}\n\nCheck the VS Code terminal for backend details.`
    );
  } finally {
    sendBtn.disabled = false;
    sendBtn.textContent = "Send →";
    messageInput.focus();
  }
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  sendMessage(messageInput.value);
});

messageInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && event.ctrlKey) {
    event.preventDefault();
    form.requestSubmit();
  }
});

document.querySelectorAll(".example").forEach((button) => {
  button.addEventListener("click", () => {
    messageInput.value = button.dataset.q;
    messageInput.focus();
  });
});

clearBtn.addEventListener("click", () => {
  history = [];
  chat.innerHTML = "";
  addMessage(
    "assistant",
    "Conversation cleared. What Power Electronics concept would you like to learn?"
  );
});

checkHealth();
messageInput.focus();
