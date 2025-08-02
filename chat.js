const socket = io();
const chatBox = document.getElementById('chat-box');
const messageInput = document.getElementById('message');
const sendButton = document.getElementById('send-button');
const fileInput = document.getElementById('file');

function appendMessage(messageHTML) {
    const div = document.createElement('div');
    div.innerHTML = messageHTML;
    chatBox.appendChild(div);
    chatBox.scrollTop = chatBox.scrollHeight;
}

sendButton.addEventListener('click', () => {
    const message = messageInput.value.trim();
    const file = fileInput.files[0];

    if (message) {
        socket.emit('chat_message', { type: 'text', content: message });
        messageInput.value = '';
    } else if (file) {
        const reader = new FileReader();
        reader.onload = () => {
            socket.emit('chat_message', {
                type: 'image',
                content: reader.result,
                filename: file.name
            });
            fileInput.value = ''; // clear input
        };
        reader.readAsDataURL(file);
    }
});

socket.on('chat_message', data => {
    if (data.type === 'text') {
        appendMessage(`<div class="message"><strong>${data.username}:</strong> ${data.content}</div>`);
    } else if (data.type === 'image') {
        appendMessage(`<div class="message"><strong>${data.username}:</strong><br><img src="${data.content}" alt="${data.filename}" style="max-width: 200px; border-radius: 6px; margin-top: 5px;"></div>`);
    }
});

socket.on('user_status', data => {
    appendMessage(`<div class="message"><em>${data.username} is ${data.status}</em></div>`);
});
