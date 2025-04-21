const chatForm = document.getElementById('chatForm');
const userInput = document.getElementById('userInput');
const chatMessages = document.getElementById('chatMessages');
const chatType = document.getElementById('chatType');
const typingIndicator = document.getElementById('typingIndicator');
const errorMessage = document.getElementById('errorMessage');
const sendButton = document.getElementById('sendButton');
let sessionId = Date.now().toString();

function showError(show = true) {
    errorMessage.style.display = show ? 'block' : 'none';
}

function setLoading(isLoading) {
    typingIndicator.classList.toggle('active', isLoading);
    sendButton.disabled = isLoading;
    userInput.disabled = isLoading;
}

function addMessage(content, isUser) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user-message' : 'assistant-message'}`;
    
    if (isUser) {
        messageDiv.textContent = content;
    } else {
        if (typeof content === 'object' && content.html) {
            messageDiv.innerHTML = content.html;
        } else {
            messageDiv.innerHTML = content;
        }
    }
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const message = userInput.value.trim();
    if (!message) return;

    showError(false);
    addMessage(message, true);
    userInput.value = '';
    setLoading(true);

    try {
        const response = await fetch('/api/chat/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                message: message,
                type: chatType.value,
                session_id: sessionId
            })
        });

        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'An error occurred');
        }

        if (data.message) {
            addMessage(data.message, false);
        } else {
            throw new Error('Invalid response from server');
        }
    } catch (error) {
        console.error('Error:', error);
        showError(true);
    } finally {
        setLoading(false);
    }
});