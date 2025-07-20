// Chat functionality
let isTyping = false;

// Initialize chat when page loads
document.addEventListener('DOMContentLoaded', function() {
    const userInput = document.getElementById('userInput');
    const sendBtn = document.getElementById('sendBtn');
    
    // Focus on input field
    userInput.focus();
    
    // Add welcome message animation
    setTimeout(() => {
        showWelcomeMessage();
    }, 500);
});

function showWelcomeMessage() {
    const welcomeMessages = [
        "Welcome! 🎉",
    ];
    
    welcomeMessages.forEach((message, index) => {
        setTimeout(() => {
            addMessage(message, 'bot');
        }, index * 1500);
    });
}

function handleEnter(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

async function sendMessage() {
    const userInput = document.getElementById('userInput');
    const message = userInput.value.trim();
    
    if (message === '' || isTyping) return;
    
    // Add user message to chat
    addMessage(message, 'user');
    userInput.value = '';
    
    // Disable input while processing
    setInputState(false);
    showTypingIndicator();
    
    try {
        const response = await fetch('/get', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message })
        });
        
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        
        const data = await response.json();
        
        // Simulate typing delay for better UX
        setTimeout(() => {
            hideTypingIndicator();
            addMessage(data.response, 'bot');
            setInputState(true);
        }, Math.random() * 1000 + 500); // Random delay between 0.5-1.5s
        
    } catch (error) {
        console.error('Error:', error);
        hideTypingIndicator();
        addMessage('Sorry, I encountered an error. Please try again! 😓', 'bot');
        setInputState(true);
    }
}

function addMessage(message, sender) {
    const chatContainer = document.getElementById('chat');
    const messageDiv = document.createElement('div');
    const currentTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    messageDiv.className = `message ${sender}-message`;
    
    const avatarDiv = document.createElement('div');
    avatarDiv.className = 'message-avatar';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    if (sender === 'user') {
        avatarDiv.innerHTML = '<i class="fas fa-user"></i>';
    } else {
        avatarDiv.innerHTML = '<i class="fas fa-robot"></i>';
    }
    
    // Process message for emoji and formatting
    const processedMessage = processMessageContent(message);
    
    contentDiv.innerHTML = `
        <p>${processedMessage}</p>
        <span class="message-time">${currentTime}</span>
    `;
    
    messageDiv.appendChild(avatarDiv);
    messageDiv.appendChild(contentDiv);
    
    chatContainer.appendChild(messageDiv);
    
    // Scroll to bottom with smooth animation
    setTimeout(() => {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }, 100);
    
    // Add message animation
    messageDiv.style.opacity = '0';
    messageDiv.style.transform = 'translateY(20px)';
    
    setTimeout(() => {
        messageDiv.style.transition = 'all 0.4s ease';
        messageDiv.style.opacity = '1';
        messageDiv.style.transform = 'translateY(0)';
    }, 50);
}

function processMessageContent(message) {
    // Add some basic text processing for better display
    // Convert **text** to bold
    message = message.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    // Convert URLs to clickable links
    const urlRegex = /(https?:\/\/[^\s]+)/g;
    message = message.replace(urlRegex, '<a href="$1" target="_blank" rel="noopener">$1</a>');
    
    // Enhance emojis with larger size
    const emojiRegex = /([\u{1F600}-\u{1F64F}]|[\u{1F300}-\u{1F5FF}]|[\u{1F680}-\u{1F6FF}]|[\u{1F700}-\u{1F77F}]|[\u{1F780}-\u{1F7FF}]|[\u{1F800}-\u{1F8FF}]|[\u{2600}-\u{26FF}]|[\u{2700}-\u{27BF}])/gu;
    message = message.replace(emojiRegex, '<span class="emoji">$1</span>');
    
    return message;
}

function showTypingIndicator() {
    const typingIndicator = document.getElementById('typingIndicator');
    typingIndicator.style.display = 'flex';
    isTyping = true;
    
    // Scroll to bottom to show typing indicator
    const chatContainer = document.getElementById('chat');
    setTimeout(() => {
        chatContainer.scrollTop = chatContainer.scrollHeight + 100;
    }, 100);
}

function hideTypingIndicator() {
    const typingIndicator = document.getElementById('typingIndicator');
    typingIndicator.style.display = 'none';
    isTyping = false;
}

function setInputState(enabled) {
    const userInput = document.getElementById('userInput');
    const sendBtn = document.getElementById('sendBtn');
    
    userInput.disabled = !enabled;
    sendBtn.disabled = !enabled;
    
    if (enabled) {
        userInput.focus();
    }
}

function clearChat() {
    const chatContainer = document.getElementById('chat');
    
    // Add confirmation dialog
    if (confirm('Are you sure you want to clear the chat history?')) {
        // Fade out animation
        chatContainer.style.opacity = '0.5';
        
        setTimeout(() => {
            chatContainer.innerHTML = `
                <div class="message bot-message">
                    <div class="message-avatar">
                        <i class="fas fa-robot"></i>
                    </div>
                    <div class="message-content">
                        <p>Chat cleared! Hello again! I'm your JARVIS. How can I assist you today? 🤖</p>
                        <span class="message-time">Just now</span>
                    </div>
                </div>
            `;
            
            chatContainer.style.opacity = '1';
            
            // Show welcome message again
            setTimeout(() => {
                showWelcomeMessage();
            }, 1000);
        }, 300);
    }
}

// Add some interactive features
document.addEventListener('DOMContentLoaded', function() {
    // Add keyboard shortcuts
    document.addEventListener('keydown', function(event) {
        // Ctrl + L to clear chat
        if (event.ctrlKey && event.key === 'l') {
            event.preventDefault();
            clearChat();
        }
        
        // Escape to focus on input
        if (event.key === 'Escape') {
            document.getElementById('userInput').focus();
        }
    });
    
    // Add click sound effect (optional)
    const sendBtn = document.getElementById('sendBtn');
    sendBtn.addEventListener('click', function() {
        // Add a subtle click effect
        this.style.transform = 'scale(0.95)';
        setTimeout(() => {
            this.style.transform = 'scale(1)';
        }, 100);
    });
    
    // Auto-resize input based on content
    const userInput = document.getElementById('userInput');
    userInput.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = Math.min(this.scrollHeight, 120) + 'px';
    });
    
    // Add placeholder animation
    let placeholderIndex = 0;
    const placeholders = [
        "Type your message...",
        "Ask me anything! 🤔",
        "Say hello! 👋",
        "Tell me a joke! 😄",
        "What's on your mind? 💭"
    ];
    
    setInterval(() => {
        if (!userInput.value && document.activeElement !== userInput) {
            userInput.placeholder = placeholders[placeholderIndex];
            placeholderIndex = (placeholderIndex + 1) % placeholders.length;
        }
    }, 3000);
});

// Add connection status indicator
function checkConnection() {
    fetch('/get', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: 'ping' })
    })
    .then(response => {
        if (response.ok) {
            updateConnectionStatus(true);
        } else {
            updateConnectionStatus(false);
        }
    })
    .catch(() => {
        updateConnectionStatus(false);
    });
}

function updateConnectionStatus(isOnline) {
    const statusDot = document.querySelector('.status-dot');
    const statusText = document.querySelector('.status');
    
    if (isOnline) {
        statusDot.style.background = '#4ade80';
        statusText.innerHTML = '<span class="status-dot"></span>Online';
    } else {
        statusDot.style.background = '#ef4444';
        statusText.innerHTML = '<span class="status-dot"></span>Offline';
    }
}

// Check connection status every 30 seconds
setInterval(checkConnection, 30000);

// Easter egg - Konami code
let konamiCode = [];
const konamiSequence = [
    'ArrowUp', 'ArrowUp', 'ArrowDown', 'ArrowDown',
    'ArrowLeft', 'ArrowRight', 'ArrowLeft', 'ArrowRight',
    'KeyB', 'KeyA'
];

document.addEventListener('keydown', function(event) {
    konamiCode.push(event.code);
    
    if (konamiCode.length > konamiSequence.length) {
        konamiCode.shift();
    }
    
    if (JSON.stringify(konamiCode) === JSON.stringify(konamiSequence)) {
        addMessage('🎉 Konami Code activated! You found the easter egg! 🎮', 'bot');
        konamiCode = [];
    }
});

// Export functions for global access
window.sendMessage = sendMessage;
window.handleEnter = handleEnter;
window.clearChat = clearChat;