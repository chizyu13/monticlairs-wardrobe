/**
 * Live Chat Widget for Montclair Wardrobe
 * Provides real-time customer support chat functionality
 */

class ChatWidget {
    constructor(productId = null) {
        this.productId = productId;
        this.sessionId = null;
        this.lastMessageId = 0;
        this.pollingInterval = null;
        this.isOpen = false;
        this.isMinimized = false;
        this.unreadCount = 0;
        
        this.init();
    }
    
    init() {
        // Check for existing session in localStorage
        const savedSession = localStorage.getItem('chat_session_id');
        if (savedSession) {
            this.sessionId = savedSession;
        }
        
        // Create chat widget HTML
        this.createWidget();
        
        // Attach event listeners
        this.attachEventListeners();
        
        // Restore session if exists
        if (this.sessionId) {
            this.restoreSession();
        }
    }
    
    createWidget() {
        const widgetHTML = `
            <div id="chat-widget" class="chat-widget">
                <!-- Floating Chat Button -->
                <button id="chat-toggle-btn" class="chat-toggle-btn">
                    <i class="fas fa-comments"></i>
                    <span class="chat-badge" id="chat-badge" style="display: none;">0</span>
                </button>
                
                <!-- Chat Window -->
                <div id="chat-window" class="chat-window" style="display: none;">
                    <!-- Chat Header -->
                    <div class="chat-header">
                        <div class="chat-header-info">
                            <h4>Live Chat Support</h4>
                            <span class="chat-status" id="chat-status">
                                <span class="status-dot"></span>
                                Online
                            </span>
                        </div>
                        <div class="chat-header-actions">
                            <button id="chat-minimize-btn" class="chat-action-btn" title="Minimize">
                                <i class="fas fa-minus"></i>
                            </button>
                            <button id="chat-close-btn" class="chat-action-btn" title="Close">
                                <i class="fas fa-times"></i>
                            </button>
                        </div>
                    </div>
                    
                    <!-- Guest Info Form (shown for non-authenticated users) -->
                    <div id="guest-form" class="guest-form" style="display: none;">
                        <h5>Start a conversation</h5>
                        <p>Please provide your details to continue</p>
                        <input type="text" id="guest-name" placeholder="Your Name" required>
                        <input type="email" id="guest-email" placeholder="Your Email" required>
                        <button id="start-chat-btn" class="btn-primary">Start Chat</button>
                    </div>
                    
                    <!-- Chat Messages -->
                    <div id="chat-messages" class="chat-messages">
                        <div class="chat-welcome">
                            <i class="fas fa-comments"></i>
                            <p>Welcome! How can we help you today?</p>
                        </div>
                    </div>
                    
                    <!-- Chat Input -->
                    <div class="chat-input-container">
                        <textarea 
                            id="chat-input" 
                            class="chat-input" 
                            placeholder="Type your message..."
                            rows="1"
                            maxlength="1000"
                        ></textarea>
                        <button id="chat-send-btn" class="chat-send-btn">
                            <i class="fas fa-paper-plane"></i>
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', widgetHTML);
    }
    
    attachEventListeners() {
        // Toggle chat window
        document.getElementById('chat-toggle-btn').addEventListener('click', () => {
            this.toggleChat();
        });
        
        // Minimize chat
        document.getElementById('chat-minimize-btn').addEventListener('click', () => {
            this.minimizeChat();
        });
        
        // Close chat
        document.getElementById('chat-close-btn').addEventListener('click', () => {
            this.closeChat();
        });
        
        // Start chat (for guests)
        document.getElementById('start-chat-btn').addEventListener('click', () => {
            this.startGuestChat();
        });
        
        // Send message
        document.getElementById('chat-send-btn').addEventListener('click', () => {
            this.sendMessage();
        });
        
        // Send on Enter (Shift+Enter for new line)
        document.getElementById('chat-input').addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Auto-resize textarea
        document.getElementById('chat-input').addEventListener('input', (e) => {
            e.target.style.height = 'auto';
            e.target.style.height = Math.min(e.target.scrollHeight, 100) + 'px';
        });
    }
    
    toggleChat() {
        const chatWindow = document.getElementById('chat-window');
        const chatToggleBtn = document.getElementById('chat-toggle-btn');
        
        if (this.isOpen) {
            chatWindow.style.display = 'none';
            this.isOpen = false;
            this.stopPolling();
        } else {
            chatWindow.style.display = 'flex';
            this.isOpen = true;
            this.isMinimized = false;
            
            // Clear unread badge
            this.unreadCount = 0;
            this.updateBadge();
            
            // Check if user needs to provide info
            if (!this.sessionId) {
                this.showGuestForm();
            } else {
                this.startPolling();
            }
            
            // Focus input
            setTimeout(() => {
                document.getElementById('chat-input').focus();
            }, 100);
        }
    }
    
    minimizeChat() {
        const chatWindow = document.getElementById('chat-window');
        chatWindow.style.display = 'none';
        this.isOpen = false;
        this.isMinimized = true;
        this.stopPolling();
    }
    
    closeChat() {
        if (confirm('Are you sure you want to close this chat?')) {
            this.minimizeChat();
            
            // Optionally close session on server
            if (this.sessionId) {
                this.closeSession();
            }
        }
    }
    
    showGuestForm() {
        // Check if user is authenticated (you may need to adjust this check)
        const isAuthenticated = document.body.dataset.authenticated === 'true';
        
        if (!isAuthenticated) {
            document.getElementById('guest-form').style.display = 'block';
            document.getElementById('chat-messages').style.display = 'none';
            document.querySelector('.chat-input-container').style.display = 'none';
        } else {
            // Authenticated user - start session immediately
            this.startSession();
        }
    }
    
    async startGuestChat() {
        const name = document.getElementById('guest-name').value.trim();
        const email = document.getElementById('guest-email').value.trim();
        
        if (!name || !email) {
            alert('Please provide your name and email');
            return;
        }
        
        // Validate email
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email)) {
            alert('Please provide a valid email address');
            return;
        }
        
        await this.startSession(name, email);
    }
    
    async startSession(guestName = null, guestEmail = null) {
        try {
            const payload = {
                product_id: this.productId
            };
            
            if (guestName && guestEmail) {
                payload.guest_name = guestName;
                payload.guest_email = guestEmail;
            }
            
            // Build URL - use /chat/start/ or /chat/start/<product_id>/
            const url = this.productId ? `/chat/start/${this.productId}/` : '/chat/start/';
            
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken(),
                },
                body: JSON.stringify(payload)
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.sessionId = data.session_id;
                localStorage.setItem('chat_session_id', this.sessionId);
                
                // Hide guest form, show chat
                document.getElementById('guest-form').style.display = 'none';
                document.getElementById('chat-messages').style.display = 'flex';
                document.querySelector('.chat-input-container').style.display = 'flex';
                
                // Start polling for messages
                this.startPolling();
                
                // Show welcome message
                if (data.created) {
                    this.addSystemMessage('Chat session started. An admin will respond shortly.');
                }
            } else {
                console.error('Failed to start chat:', data.error);
                alert('Failed to start chat: ' + data.error);
            }
        } catch (error) {
            console.error('Error starting chat:', error);
            console.error('Response status:', error.response?.status);
            alert('Failed to start chat. Please check your internet connection and try again.');
        }
    }
    
    async restoreSession() {
        // Load existing messages
        await this.pollMessages();
        
        // Show chat interface
        document.getElementById('guest-form').style.display = 'none';
        document.getElementById('chat-messages').style.display = 'flex';
        document.querySelector('.chat-input-container').style.display = 'flex';
    }
    
    async sendMessage() {
        const input = document.getElementById('chat-input');
        const message = input.value.trim();
        
        if (!message) return;
        
        if (!this.sessionId) {
            alert('Please start a chat session first');
            return;
        }
        
        try {
            const response = await fetch(`/chat/send/${this.sessionId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken(),
                },
                body: JSON.stringify({ message })
            });
            
            // Check if response is ok
            if (!response.ok) {
                const errorText = await response.text();
                console.error('Server error:', response.status, errorText);
                throw new Error(`Server returned ${response.status}: ${errorText}`);
            }
            
            const data = await response.json();
            
            if (data.success) {
                // Clear input
                input.value = '';
                input.style.height = 'auto';
                
                // Add message to UI immediately
                this.addMessage({
                    sender_name: 'You',
                    message: message,
                    is_admin: false,
                    created_at: new Date().toISOString()
                });
                
                // Update last message ID
                this.lastMessageId = data.message_id;
            } else {
                console.error('Failed to send message:', data.error);
                alert('Failed to send message: ' + data.error);
            }
        } catch (error) {
            console.error('Error sending message:', error);
            alert('Failed to send message. Please check your internet connection and try again.');
        }
    }
    
    startPolling() {
        if (this.pollingInterval) return;
        
        // Poll every 3 seconds
        this.pollingInterval = setInterval(() => {
            this.pollMessages();
        }, 3000);
        
        // Initial poll
        this.pollMessages();
    }
    
    stopPolling() {
        if (this.pollingInterval) {
            clearInterval(this.pollingInterval);
            this.pollingInterval = null;
        }
    }
    
    async pollMessages() {
        if (!this.sessionId) return;
        
        try {
            const response = await fetch(
                `/chat/messages/${this.sessionId}/?last_message_id=${this.lastMessageId}`
            );
            
            const data = await response.json();
            
            if (data.success && data.messages.length > 0) {
                data.messages.forEach(msg => {
                    this.addMessage(msg);
                    this.lastMessageId = Math.max(this.lastMessageId, msg.id);
                });
                
                // Update unread count if minimized
                if (this.isMinimized || !this.isOpen) {
                    this.unreadCount += data.messages.filter(m => m.is_admin).length;
                    this.updateBadge();
                }
                
                // Play notification sound for admin messages
                if (data.messages.some(m => m.is_admin)) {
                    this.playNotificationSound();
                }
            }
        } catch (error) {
            console.error('Error polling messages:', error);
        }
    }
    
    addMessage(message) {
        const messagesContainer = document.getElementById('chat-messages');
        const isOwnMessage = !message.is_admin;
        
        const messageEl = document.createElement('div');
        messageEl.className = `chat-message ${isOwnMessage ? 'customer' : 'admin'}`;
        
        const time = new Date(message.created_at).toLocaleTimeString([], { 
            hour: '2-digit', 
            minute: '2-digit' 
        });
        
        messageEl.innerHTML = `
            <div class="message-bubble">
                <div class="message-sender">${message.sender_name}</div>
                <div class="message-text">${this.escapeHtml(message.message)}</div>
                <div class="message-time">${time}</div>
            </div>
        `;
        
        messagesContainer.appendChild(messageEl);
        
        // Scroll to bottom
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
    
    addSystemMessage(text) {
        const messagesContainer = document.getElementById('chat-messages');
        
        const messageEl = document.createElement('div');
        messageEl.className = 'chat-message system';
        messageEl.innerHTML = `
            <div class="message-bubble">
                <div class="message-text">${this.escapeHtml(text)}</div>
            </div>
        `;
        
        messagesContainer.appendChild(messageEl);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
    
    updateBadge() {
        const badge = document.getElementById('chat-badge');
        if (this.unreadCount > 0) {
            badge.textContent = this.unreadCount > 9 ? '9+' : this.unreadCount;
            badge.style.display = 'block';
        } else {
            badge.style.display = 'none';
        }
    }
    
    playNotificationSound() {
        // Simple notification sound using Web Audio API
        try {
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const oscillator = audioContext.createOscillator();
            const gainNode = audioContext.createGain();
            
            oscillator.connect(gainNode);
            gainNode.connect(audioContext.destination);
            
            oscillator.frequency.value = 800;
            oscillator.type = 'sine';
            
            gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
            gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);
            
            oscillator.start(audioContext.currentTime);
            oscillator.stop(audioContext.currentTime + 0.5);
        } catch (error) {
            console.log('Could not play notification sound:', error);
        }
    }
    
    async closeSession() {
        if (!this.sessionId) return;
        
        try {
            await fetch(`/chat/close/${this.sessionId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken(),
                }
            });
            
            // Clear session
            this.sessionId = null;
            localStorage.removeItem('chat_session_id');
            this.lastMessageId = 0;
            this.stopPolling();
            
            // Clear messages
            document.getElementById('chat-messages').innerHTML = `
                <div class="chat-welcome">
                    <i class="fas fa-comments"></i>
                    <p>Chat session ended. Refresh to start a new chat.</p>
                </div>
            `;
        } catch (error) {
            console.error('Error closing session:', error);
        }
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    getCsrfToken() {
        // Get CSRF token from cookie
        const name = 'csrftoken';
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
}

// Initialize chat widget when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Check if we're on a product page
    const productId = document.body.dataset.productId || null;
    
    // Initialize chat widget
    window.chatWidget = new ChatWidget(productId);
});
