"use strict";

// =========================================================
// KASHVI — CHAT INTERFACE
// =========================================================

const form = document.getElementById("chat-form");
const input = document.getElementById("message");
const chat = document.getElementById("chat");
const sendButton = document.getElementById("send-button");
const welcome = document.getElementById("welcome");

const sidebar = document.querySelector(".sidebar");
const main = document.querySelector(".main");
const sidebarToggle = document.getElementById("sidebar-toggle");
const sidebarBackdrop = document.getElementById("sidebar-backdrop");
const newChat = document.getElementById("new-chat");

let waiting = false;
let activeController = null;


// =========================================================
// MESSAGE CREATION
// =========================================================

function addMessage(sender, text, type) {
    const message = document.createElement("div");
    message.className = `message ${type}`;

    const senderElement = document.createElement("div");
    senderElement.className = "sender";
    senderElement.textContent = sender;

    const bubble = document.createElement("div");
    bubble.className = "bubble";
    bubble.textContent = text;

    message.appendChild(senderElement);
    message.appendChild(bubble);

    chat.appendChild(message);
    scrollToBottom();

    return message;
}


// =========================================================
// STREAMING MESSAGE
// =========================================================

function createStreamingMessage() {
    const message = document.createElement("div");
    message.className = "message kashvi";

    const sender = document.createElement("div");
    sender.className = "sender";
    sender.textContent = "Kashvi";

    const bubble = document.createElement("div");
    bubble.className = "bubble";
    bubble.textContent = "";

    message.appendChild(sender);
    message.appendChild(bubble);

    chat.appendChild(message);
    scrollToBottom();

    return bubble;
}


// =========================================================
// THINKING INDICATOR
// =========================================================

function showTyping() {
    removeTyping();

    const message = document.createElement("div");
    message.id = "typing-message";
    message.className = "message kashvi";

    const sender = document.createElement("div");
    sender.className = "sender";
    sender.textContent = "Kashvi";

    const typing = document.createElement("div");
    typing.className = "typing";

    typing.setAttribute("role", "status");
    typing.setAttribute("aria-label", "Kashvi is thinking");

    for (let i = 0; i < 3; i++) {
        const dot = document.createElement("span");

        dot.setAttribute("aria-hidden", "true");

        typing.appendChild(dot);
    }

    message.appendChild(sender);
    message.appendChild(typing);

    chat.appendChild(message);
    scrollToBottom();
}


function removeTyping() {
    const existing = document.getElementById("typing-message");

    if (existing) {
        existing.remove();
    }
}


// =========================================================
// UI HELPERS
// =========================================================

function scrollToBottom() {
    chat.scrollTop = chat.scrollHeight;
}


function resizeInput() {
    input.style.height = "auto";

    input.style.height =
        Math.min(input.scrollHeight, 160) + "px";
}


function setWaitingState(state) {
    waiting = state;

    sendButton.disabled = state;
    input.disabled = state;

    if (state) {
        sendButton.setAttribute("aria-busy", "true");
    } else {
        sendButton.removeAttribute("aria-busy");
    }
}


// =========================================================
// STREAM RESPONSE
// =========================================================

async function streamResponse(message) {
    activeController = new AbortController();

    const response = await fetch("/api/chat/stream", {
        method: "POST",

        headers: {
            "Content-Type": "application/json",
            "Accept": "text/event-stream, text/plain"
        },

        body: JSON.stringify({
            message: message
        }),

        signal: activeController.signal
    });

    if (!response.ok) {
        throw new Error(
            `Server returned HTTP ${response.status}`
        );
    }

    if (!response.body) {
        throw new Error(
            "The server did not provide a readable response stream."
        );
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    let bubble = null;
    let bubbleText = null;
    const responseChunks = [];

    try {
        while (true) {
            const result = await reader.read();

            if (result.done) {
                break;
            }

            const chunk = decoder.decode(
                result.value,
                { stream: true }
            );

            if (!chunk) {
                continue;
            }

            // Ignore whitespace-only chunks until real text arrives.
            // The thinking indicator remains visible in the meantime.
            if (!bubble && !chunk.trim()) {
                continue;
            }

            // Replace the thinking indicator only when actual
            // response content starts arriving.
            if (!bubble) {
                removeTyping();
                bubble = createStreamingMessage();
                bubbleText = document.createTextNode("");
                bubble.appendChild(bubbleText);
            }

            responseChunks.push(chunk);
            bubbleText.appendData(chunk);

            scrollToBottom();
        }

        // Flush any remaining decoder content.
        const remaining = decoder.decode();

        if (remaining) {
            if (!bubble && remaining.trim()) {
                removeTyping();
                bubble = createStreamingMessage();
                bubbleText = document.createTextNode("");
                bubble.appendChild(bubbleText);
            }

            if (bubbleText) {
                responseChunks.push(remaining);
                bubbleText.appendData(remaining);

                scrollToBottom();
            }
        }

        // Detect an empty response rather than leaving the UI blank.
        const fullResponse = responseChunks.join("");

        if (!fullResponse.trim()) {
            if (bubble) {
                bubble.closest(".message")?.remove();
            }

            throw new Error(
                "The server finished without returning response text."
            );
        }

        return fullResponse;

    } finally {
        reader.releaseLock();
    }
}


// =========================================================
// SUBMIT MESSAGE
// =========================================================

form.addEventListener("submit", async (event) => {
    event.preventDefault();

    if (waiting) {
        return;
    }

    const message = input.value.trim();

    if (!message) {
        return;
    }

    // Remove the welcome screen when the first message is sent.
    if (welcome) {
        welcome.remove();
    }

    addMessage("You", message, "user");

    input.value = "";
    resizeInput();

    setWaitingState(true);

    // Display the indicator immediately, before the network request.
    showTyping();

    try {
        await streamResponse(message);

    } catch (error) {
        removeTyping();

        if (error.name === "AbortError") {
            return;
        }

        console.error("Kashvi streaming error:", error);

        addMessage(
            "Kashvi",
            "I'm sorry, something went wrong while processing that. Please try again.",
            "kashvi"
        );

    } finally {
        removeTyping();

        activeController = null;

        setWaitingState(false);

        input.focus();
    }
});


// =========================================================
// INPUT BEHAVIOR
// =========================================================

input.addEventListener("input", resizeInput);


input.addEventListener("keydown", (event) => {
    if (
        event.key === "Enter" &&
        !event.shiftKey &&
        !event.isComposing
    ) {
        event.preventDefault();
        form.requestSubmit();
    }
});


// =========================================================
// SUGGESTIONS
// =========================================================

document.addEventListener("click", (event) => {
    const button = event.target.closest(".suggestion");

    if (!button) {
        return;
    }

    input.value = button.textContent.trim();

    resizeInput();
    input.focus();
});


// =========================================================
// NEW CHAT
// =========================================================

if (newChat) {
    newChat.addEventListener("click", () => {
        window.location.reload();
    });
}


// =========================================================
// SIDEBAR
// =========================================================

function setSidebarOpen(isOpen, restoreFocus = true) {
    if (!sidebar || !sidebarToggle || !sidebarBackdrop) {
        return;
    }

    sidebar.classList.toggle("open", isOpen);
    sidebarBackdrop.hidden = !isOpen;
    sidebarToggle.setAttribute("aria-expanded", String(isOpen));
    sidebarToggle.setAttribute(
        "aria-label",
        isOpen ? "Close menu" : "Open menu"
    );
    document.body.classList.toggle("menu-open", isOpen);

    if (main) {
        main.inert = isOpen;
    }

    if (isOpen) {
        newChat?.focus();
    } else if (restoreFocus) {
        sidebarToggle.focus();
    }
}


if (sidebarToggle && sidebar && sidebarBackdrop) {
    sidebarToggle.addEventListener("click", () => {
        setSidebarOpen(!sidebar.classList.contains("open"));
    });

    sidebarBackdrop.addEventListener("click", () => {
        setSidebarOpen(false);
    });

    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape" && sidebar.classList.contains("open")) {
            setSidebarOpen(false);
            return;
        }

        if (event.key === "Tab" && sidebar.classList.contains("open")) {
            const menuItems = sidebar.querySelectorAll(
                "button:not([disabled]), a[href], input:not([disabled]), textarea:not([disabled])"
            );

            if (menuItems.length === 1) {
                event.preventDefault();
                menuItems[0].focus();
            }
        }
    });

    window.matchMedia("(min-width: 701px)").addEventListener("change", (event) => {
        if (event.matches && sidebar.classList.contains("open")) {
            setSidebarOpen(false, false);
        }
    });
}
