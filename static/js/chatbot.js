document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chatForm');
    const chatInput = document.getElementById('chatInput');
    const sendBtn = document.getElementById('sendBtn');
    const messagesContainer = document.getElementById('messagesContainer');
    const searchChatsInput = document.getElementById('searchChatsInput');
    const historyList = document.getElementById('historyList');
    
    // Auto-scroll to bottom of chat with slight delay for browser repaint
    function scrollToBottom() {
        if (messagesContainer) {
            setTimeout(() => {
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
            }, 50);
        }
    }
    
    // Parse existing messages on load
    const existingBotMessages = document.querySelectorAll('.chat-markdown-text');
    existingBotMessages.forEach(msg => {
        msg.innerHTML = parseMarkdown(msg.textContent.trim());
    });
    
    // Initial scroll on load
    if (messagesContainer) {
        scrollToBottom();
    }
    if (chatInput) {
        chatInput.focus({ preventScroll: true });
    }

    // Markdown Parser Helper
    function parseMarkdown(text) {
        if (!text) return '';
        
        let html = text;
        
        // 1. Escaping basic HTML to prevent XSS
        html = html
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;");
            
        // 2. Bold text formatting (**text** -> <strong>text</strong>)
        html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        
        // 3. Headings formatting (### text -> <h3>text</h3>)
        html = html.replace(/^### (.*?)$/gm, '<h3>$1</h3>');
        html = html.replace(/^## (.*?)$/gm, '<h2>$1</h2>');
        html = html.replace(/^# (.*?)$/gm, '<h1>$1</h1>');
        
        // 4. Bullet lists (- item or * item -> <li>item</li>)
        html = html.replace(/^\s*[-*]\s+(.*?)$/gm, '<li>$1</li>');
        html = html.replace(/(<li>.*?<\/li>)+/g, '<ul>$&</ul>');
        
        // 5. Code blocks (```code``` -> <pre><code>code</code></pre>)
        html = html.replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>');
        
        // 6. Inline code (`code` -> <code>code</code>)
        html = html.replace(/`(.*?)`/g, '<code>$1</code>');
        
        // 7. Paragraph splits (double newlines)
        html = html.replace(/\n\n/g, '</p><p>');
        html = html.replace(/\n/g, '<br>');
        
        if (!html.startsWith('<h') && !html.startsWith('<u') && !html.startsWith('<p')) {
            html = '<p>' + html + '</p>';
        }
        
        return html;
    }

    // Format Timestamp Helper
    function formatTime(isoString) {
        try {
            const date = new Date(isoString.replace(' ', 'T'));
            return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        } catch (e) {
            return 'Just now';
        }
    }

    // Create Chat Message Bubble Node
    function appendMessage(sender, text, timestamp, id, saved = 0) {
        const row = document.createElement('div');
        row.className = `message-row ${sender === 'user' ? 'user-row' : 'bot-row'}`;
        if (id) row.setAttribute('data-id', id);
        
        const bubble = document.createElement('div');
        bubble.className = 'message-bubble';
        
        if (sender === 'user') {
            bubble.textContent = text;
        } else {
            // Append formatted HTML and wrap inside chat-markdown-text for consistency
            const mdWrapper = document.createElement('div');
            mdWrapper.className = 'chat-markdown-text';
            mdWrapper.innerHTML = parseMarkdown(text);
            bubble.appendChild(mdWrapper);
        }
        
        const meta = document.createElement('div');
        meta.className = 'message-meta';
        meta.innerHTML = `<span>${formatTime(timestamp)}</span>`;
        
        if (sender === 'bot' && id) {
            const saveIconClass = saved ? 'fa-solid fa-bookmark' : 'fa-regular fa-bookmark';
            const actions = document.createElement('span');
            actions.className = 'message-actions';
            actions.innerHTML = `
                <i class="${saveIconClass} save-btn" title="${saved ? 'Unsave chat' : 'Save chat'}" data-id="${id}"></i>
                <i class="fa-regular fa-trash-can delete-btn" title="Delete chat" data-id="${id}" style="margin-left: 10px;"></i>
            `;
            meta.appendChild(actions);
        }
        
        bubble.appendChild(meta);
        row.appendChild(bubble);
        messagesContainer.appendChild(row);
        scrollToBottom();
    }

    // Load Typing Loader indicator
    let loaderNode = null;
    function showTypingLoader() {
        const row = document.createElement('div');
        row.className = 'message-row bot-row loader-row';
        
        const bubble = document.createElement('div');
        bubble.className = 'message-bubble';
        
        const loader = document.createElement('div');
        loader.className = 'typing-indicator';
        loader.innerHTML = `
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
        `;
        
        bubble.appendChild(loader);
        row.appendChild(bubble);
        messagesContainer.appendChild(row);
        loaderNode = row;
        scrollToBottom();
    }

    function removeTypingLoader() {
        if (loaderNode) {
            loaderNode.remove();
            loaderNode = null;
        }
    }

    // Submit user message
    if (chatForm) {
        chatForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const message = chatInput.value.trim();
            if (!message) return;
            
            chatInput.value = '';
            chatInput.style.height = 'auto'; // Reset textarea height
            
            // Disable inputs during network request
            chatInput.disabled = true;
            if (sendBtn) sendBtn.disabled = true;
            
            // Append user message instantly
            const now = new Date().toISOString();
            appendMessage('user', message, now);
            
            // Show bot typing loader
            showTypingLoader();
            
            try {
                const response = await fetch('/chatbot/send', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: message })
                });
                
                const data = await response.json();
                
                removeTypingLoader();
                
                // Re-enable inputs
                chatInput.disabled = false;
                if (sendBtn) sendBtn.disabled = false;
                chatInput.focus({ preventScroll: true });
                
                if (data.error) {
                    appendMessage('bot', `Sorry, I encountered an error: ${data.error}`, now);
                } else {
                    appendMessage('bot', data.response, data.timestamp, data.id, data.saved);
                    // Add item to sidebar history if not present
                    refreshHistoryList();
                }
            } catch (err) {
                removeTypingLoader();
                // Re-enable inputs
                chatInput.disabled = false;
                if (sendBtn) sendBtn.disabled = false;
                chatInput.focus({ preventScroll: true });
                
                appendMessage('bot', 'An unexpected connection error occurred. Please try again.', now);
            }
        });
        
        // Auto-grow textarea
        chatInput.addEventListener('input', () => {
            chatInput.style.height = 'auto';
            chatInput.style.height = (chatInput.scrollHeight) + 'px';
        });
        
        // Submit on enter (Shift+Enter for newline)
        chatInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                chatForm.dispatchEvent(new Event('submit'));
            }
        });
    }

    // Event Delegation for Save and Delete buttons
    if (messagesContainer) {
        messagesContainer.addEventListener('click', async (e) => {
            if (e.target.classList.contains('save-btn')) {
                const chatID = e.target.getAttribute('data-id');
                const isSaved = e.target.classList.contains('fa-solid');
                
                try {
                    const response = await fetch(`/chatbot/save/${chatID}`, { method: 'POST' });
                    const data = await response.json();
                    if (data.success) {
                        if (isSaved) {
                            e.target.className = 'fa-regular fa-bookmark save-btn';
                            e.target.title = 'Save chat';
                        } else {
                            e.target.className = 'fa-solid fa-bookmark save-btn';
                            e.target.title = 'Unsave chat';
                        }
                    }
                } catch (err) {
                    console.error('Failed to toggle saved status:', err);
                }
            } else if (e.target.classList.contains('delete-btn')) {
                const chatID = e.target.getAttribute('data-id');
                if (confirm('Are you sure you want to delete this chat block?')) {
                    try {
                        const response = await fetch(`/chatbot/delete/${chatID}`, { method: 'DELETE' });
                        const data = await response.json();
                        if (data.success) {
                            // Remove bubble row from interface
                            const row = e.target.closest('.message-row');
                            // Also remove corresponding user question row if it immediately precedes this bot row
                            const prevRow = row.previousElementSibling;
                            if (prevRow && prevRow.classList.contains('user-row')) {
                                prevRow.remove();
                            }
                            row.remove();
                            refreshHistoryList();
                        }
                    } catch (err) {
                        console.error('Failed to delete chat:', err);
                    }
                }
            }
        });
    }

    // History Sidebar Search & Refresh
    async function refreshHistoryList(query = '') {
        if (!historyList) return;
        try {
            const url = query ? `/chatbot/search?q=${encodeURIComponent(query)}` : '/chatbot/search';
            const response = await fetch(url);
            const chats = await response.json();
            
            historyList.innerHTML = '';
            
            if (chats.length === 0) {
                historyList.innerHTML = '<li class="text-center" style="font-size:0.8rem;color:var(--text-muted);">No history</li>';
                return;
            }
            
            chats.slice().reverse().forEach(c => {
                const li = document.createElement('li');
                li.className = 'history-item';
                
                // Safe element construction to avoid quote escaping injection issues
                const textSpan = document.createElement('span');
                textSpan.className = 'history-item-text';
                textSpan.title = c.message;
                textSpan.textContent = c.message;
                
                const actionsSpan = document.createElement('span');
                actionsSpan.className = 'history-item-actions';
                actionsSpan.innerHTML = `
                    <button class="history-btn delete-btn" data-id="${c.id}" title="Delete"><i class="fa-regular fa-trash-can delete-btn" data-id="${c.id}"></i></button>
                `;
                
                li.appendChild(textSpan);
                li.appendChild(actionsSpan);
                
                // Click to scroll to message bubble if it is rendered on screen
                li.addEventListener('click', (e) => {
                    if (e.target.classList.contains('delete-btn') || e.target.closest('.delete-btn')) return;
                    const rendered = document.querySelector(`.message-row[data-id="${c.id}"]`);
                    if (rendered) {
                        rendered.scrollIntoView({ behavior: 'smooth' });
                        const bubble = rendered.querySelector('.message-bubble');
                        if (bubble) {
                            bubble.style.borderColor = 'var(--primary)';
                            setTimeout(() => {
                                bubble.style.borderColor = 'var(--border-color)';
                            }, 2000);
                        }
                    } else {
                        alert(`Message snippet: "${c.message.substring(0, 30)}..."`);
                    }
                });
                
                historyList.appendChild(li);
            });
        } catch (err) {
            console.error('History refresh failed:', err);
        }
    }

    // Hook search keyup event
    if (searchChatsInput) {
        let debounceTimer;
        searchChatsInput.addEventListener('input', () => {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => {
                refreshHistoryList(searchChatsInput.value.trim());
            }, 300); // 300ms debounce
        });
    }
});
