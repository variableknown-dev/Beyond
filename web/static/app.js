"use strict";

// =========================================================
// BEYOND — CHAT INTERFACE
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
const attachImageButton = document.getElementById("attach-image");
const imageFileInput = document.getElementById("image-file");
const imagePreview = document.getElementById("image-preview");
const imagePreviewThumbnail = document.getElementById("image-preview-thumbnail");
const imageFileName = document.getElementById("image-file-name");
const removeImageButton = document.getElementById("remove-image");
const imageError = document.getElementById("image-error");

let waiting = false;
let activeController = null;
let selectedImage = null;
let imagePreviewUrl = null;
const serviceErrorMessage = "Sorry, but we are currently experiencing a few errors in our code. We are working to resolve them promptly. We apologize for the inconvenience.";


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
    message.className = "message beyond";

    const sender = document.createElement("div");
    sender.className = "sender";
    sender.textContent = "Beyond";

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
    message.className = "message beyond";

    const sender = document.createElement("div");
    sender.className = "sender";
    sender.textContent = "Beyond";

    const typing = document.createElement("div");
    typing.className = "typing";

    typing.setAttribute("role", "status");
    typing.setAttribute("aria-label", "Beyond is thinking");

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
    if (attachImageButton) attachImageButton.disabled = state;
    if (removeImageButton) removeImageButton.disabled = state;

    if (state) {
        sendButton.setAttribute("aria-busy", "true");
    } else {
        sendButton.removeAttribute("aria-busy");
    }
}


if (attachImageButton && imageFileInput) {
    attachImageButton.addEventListener("click", () => imageFileInput.click());

    imageFileInput.addEventListener("change", () => {
        imageError.hidden = true;
        imageError.textContent = "";
        const file = imageFileInput.files?.[0];
        if (!file) return;

        const allowedTypes = ["image/png", "image/jpeg", "image/webp"];
        if (!allowedTypes.includes(file.type)) {
            imageError.textContent = "Choose a PNG, JPEG, or WebP image.";
            imageError.hidden = false;
            clearSelectedImage();
            return;
        }
        if (file.size > 8 * 1024 * 1024) {
            imageError.textContent = "Images must be 8 MB or smaller.";
            imageError.hidden = false;
            clearSelectedImage();
            return;
        }

        clearSelectedImage();
        imageError.hidden = true;
        selectedImage = file;
        imagePreviewUrl = URL.createObjectURL(file);
        imagePreviewThumbnail.src = imagePreviewUrl;
        imageFileName.textContent = file.name;
        imagePreview.hidden = false;
    });
}

removeImageButton?.addEventListener("click", () => {
    clearSelectedImage();
    imageError.hidden = true;
});


// =========================================================
// STREAM RESPONSE
// =========================================================

function hasExplicitPlace(message) {
    const match = message.match(/\b(?:in|at|for|near)\s+([^,?.!]+)/i);
    if (!match) return false;
    const place = match[1].trim().toLowerCase();
    return !/^(?:here|there|me|my\s+(?:location|area)|tomorrow|today|tonight|this\s+week|next\s+few\s+days|celsius|fahrenheit)$/.test(place);
}


function needsLocalTime(message) {
    return /\b(?:time|date|today|tomorrow)\b/i.test(message);
}


function needsCoordinates(message) {
    const text = message.toLowerCase();
    const weather = /\b(?:weather|forecast|temperature|rain|snow|humidity|wind)\b/.test(text)
        && !/\b(?:yesterday|last\s+(?:week|month|year)|historical|past\s+weather)\b/.test(text);
    const nearby = /\b(?:near me|around me|in my area|local news|nearby news)\b/.test(text);
    return (weather || nearby) && !hasExplicitPlace(message);
}


async function getLocationContext(message) {
    const location = {};
    if (needsLocalTime(message)) {
        try {
            location.timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
        } catch (error) {
            console.warn("Could not read browser timezone:", error);
        }
    }

    if (needsCoordinates(message) && navigator.geolocation) {
        try {
            const position = await new Promise((resolve, reject) => {
                navigator.geolocation.getCurrentPosition(resolve, reject, {
                    enableHighAccuracy: false,
                    timeout: 8000,
                    maximumAge: 120000
                });
            });
            location.latitude = position.coords.latitude;
            location.longitude = position.coords.longitude;
        } catch (error) {
            // The user can deny permission; the server will then ask for a city.
        }
    }

    return Object.keys(location).length ? location : null;
}


function readImageAsBase64(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => {
            const dataUrl = String(reader.result || "");
            const comma = dataUrl.indexOf(",");
            if (comma < 0) {
                reject(new Error("Could not read the selected image."));
                return;
            }
            resolve(dataUrl.slice(comma + 1));
        };
        reader.onerror = () => reject(new Error("Could not read the selected image."));
        reader.readAsDataURL(file);
    });
}


function clearSelectedImage() {
    selectedImage = null;
    imageFileInput.value = "";
    imagePreview.hidden = true;
    imagePreviewThumbnail.removeAttribute("src");
    imageFileName.textContent = "";
    if (imagePreviewUrl) {
        URL.revokeObjectURL(imagePreviewUrl);
        imagePreviewUrl = null;
    }
}


async function streamResponse(message, location, image) {
    activeController = new AbortController();

    const response = await fetch("/api/chat/stream", {
        method: "POST",

        headers: {
            "Content-Type": "application/json",
            "Accept": "text/event-stream, text/plain"
        },

        body: JSON.stringify({
            message: message,
            location: location,
            image: image
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

    const typedMessage = input.value.trim();
    const message = typedMessage || (selectedImage ? "Describe this image." : "");

    if (!message) {
        return;
    }

    // Remove the welcome screen when the first message is sent.
    if (welcome) {
        welcome.remove();
    }

    const visibleMessage = selectedImage
        ? `${message}\n[Image attached: ${selectedImage.name}]`
        : message;
    addMessage("You", visibleMessage, "user");

    input.value = "";
    resizeInput();

    setWaitingState(true);

    // Display the indicator immediately, before the network request.
    showTyping();

    try {
        const location = selectedImage ? null : await getLocationContext(message);
        const image = selectedImage
            ? { mime_type: selectedImage.type, data: await readImageAsBase64(selectedImage) }
            : null;
        await streamResponse(message, location, image);
        clearSelectedImage();

    } catch (error) {
        removeTyping();

        if (error.name === "AbortError") {
            return;
        }

        console.error("Beyond streaming error:", error);

        input.value = typedMessage;
        resizeInput();

        addMessage(
            "Beyond",
            serviceErrorMessage,
            "beyond"
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
    newChat.addEventListener("click", async () => {
        newChat.disabled = true;

        try {
            await fetch("/api/chat/reset", {
                method: "POST",
                credentials: "same-origin"
            });
        } catch (error) {
            console.error("Beyond chat reset error:", error);
        }

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
