const form = document.getElementById("chat-form");
const input = document.getElementById("message");
const chat = document.getElementById("chat");
const sendButton = document.getElementById("send-button");
const welcome = document.getElementById("welcome");

const sidebar = document.querySelector(".sidebar");
const sidebarToggle = document.getElementById("sidebar-toggle");
const newChat = document.getElementById("new-chat");

let waiting = false;


/* =========================================
   ADD MESSAGE
========================================= */

function addMessage(sender, text, type) {

    const message =
        document.createElement("div");

    message.className =
        `message ${type}`;


    const senderElement =
        document.createElement("div");

    senderElement.className =
        "sender";

    senderElement.textContent =
        sender;


    const bubble =
        document.createElement("div");

    bubble.className =
        "bubble";

    bubble.textContent =
        text;


    message.appendChild(
        senderElement
    );

    message.appendChild(
        bubble
    );

    chat.appendChild(
        message
    );

    scrollToBottom();
}


/* =========================================
   CREATE STREAMING MESSAGE
========================================= */

function createStreamingMessage() {

    const message =
        document.createElement("div");

    message.className =
        "message aarya";


    const sender =
        document.createElement("div");

    sender.className =
        "sender";

    sender.textContent =
        "Aarya";


    const bubble =
        document.createElement("div");

    bubble.className =
        "bubble";

    bubble.textContent =
        "";


    message.appendChild(
        sender
    );

    message.appendChild(
        bubble
    );

    chat.appendChild(
        message
    );

    scrollToBottom();


    return bubble;
}


/* =========================================
   TYPING INDICATOR
========================================= */

function showTyping() {

    removeTyping();

    const message =
        document.createElement("div");

    message.id =
        "typing-message";

    message.className =
        "message aarya";


    const sender =
        document.createElement("div");

    sender.className =
        "sender";

    sender.textContent =
        "Aarya";


    const typing =
        document.createElement("div");

    typing.className =
        "typing";


    for (
        let i = 0;
        i < 3;
        i++
    ) {

        const dot =
            document.createElement("span");

        typing.appendChild(
            dot
        );
    }


    message.appendChild(
        sender
    );

    message.appendChild(
        typing
    );

    chat.appendChild(
        message
    );

    scrollToBottom();
}


function removeTyping() {

    const existing =
        document.getElementById(
            "typing-message"
        );

    if (existing) {

        existing.remove();

    }
}


/* =========================================
   SCROLL
========================================= */

function scrollToBottom() {

    chat.scrollTo({

        top:
            chat.scrollHeight,

        behavior:
            "smooth"

    });
}


/* =========================================
   TEXTAREA AUTO RESIZE
========================================= */

function resizeInput() {

    input.style.height =
        "auto";

    input.style.height =
        Math.min(
            input.scrollHeight,
            160
        ) + "px";
}


input.addEventListener(
    "input",
    resizeInput
);


/* =========================================
   STREAM RESPONSE
========================================= */

async function streamResponse(message) {

    const response =
        await fetch(
            "/api/chat/stream",
            {

                method:
                    "POST",

                headers: {

                    "Content-Type":
                        "application/json"

                },

                body:
                    JSON.stringify({
                        message:
                            message
                    })

            }
        );


    if (!response.ok) {

        throw new Error(
            `Server returned ${response.status}`
        );

    }


    if (!response.body) {

        throw new Error(
            "Streaming is not supported by this browser."
        );

    }


    const reader =
        response.body.getReader();


    const decoder =
        new TextDecoder();


    const bubble =
        createStreamingMessage();


    let fullResponse =
        "";


    while (true) {

        const {
            value,
            done
        } =
            await reader.read();


        if (done) {
            break;
        }


        const chunk =
            decoder.decode(
                value,
                {
                    stream:
                        true
                }
            );


        if (!chunk) {
            continue;
        }


        fullResponse +=
            chunk;


        bubble.textContent =
            fullResponse;


        scrollToBottom();

    }


    return fullResponse;
}


/* =========================================
   SUBMIT
========================================= */

form.addEventListener(
    "submit",
    async (event) => {

        event.preventDefault();


        if (waiting) {
            return;
        }


        const message =
            input.value.trim();


        if (!message) {
            return;
        }


        if (welcome) {

            welcome.remove();

        }


        addMessage(
            "You",
            message,
            "user"
        );


        input.value =
            "";

        resizeInput();


        waiting =
            true;

        sendButton.disabled =
            true;


        showTyping();


        try {

            await streamResponse(
                message
            );


            removeTyping();


        } catch (error) {

            console.error(
                "Aarya streaming error:",
                error
            );


            removeTyping();


            addMessage(
                "Aarya",
                "I'm sorry, something went wrong while processing that.",
                "aarya"
            );

        } finally {

            waiting =
                false;

            sendButton.disabled =
                false;

            input.focus();

        }

    }
);


/* =========================================
   ENTER TO SEND
========================================= */

input.addEventListener(
    "keydown",
    (event) => {

        if (
            event.key === "Enter" &&
            !event.shiftKey
        ) {

            event.preventDefault();

            form.requestSubmit();

        }

    }
);


/* =========================================
   SUGGESTIONS
========================================= */

document.addEventListener(
    "click",
    (event) => {

        const button =
            event.target.closest(
                ".suggestion"
            );


        if (!button) {
            return;
        }


        input.value =
            button.textContent.trim();


        resizeInput();

        input.focus();

    }
);


/* =========================================
   NEW CHAT
========================================= */

newChat.addEventListener(
    "click",
    () => {

        chat.innerHTML =
            "";

        window.location.reload();

    }
);


/* =========================================
   MOBILE SIDEBAR
========================================= */

if (sidebarToggle) {

    sidebarToggle.addEventListener(
        "click",
        () => {

            sidebar.classList.toggle(
                "open"
            );

        }
    );

}
