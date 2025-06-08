"""
Chatbot HTML Interface
Provides the HTML template for the Angel One chatbot interface
"""


def get_chatbot_html():
    """Returns the HTML template for the chatbot interface"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Angel Assist</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }

            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 20px;
            }

            .container {
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(10px);
                border-radius: 20px;
                padding: 30px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                width: 100%;
                max-width: 900px;
                min-height: 600px;
                display: flex;
                flex-direction: column;
            }

            .header {
                text-align: center;
                margin-bottom: 30px;
                padding-bottom: 20px;
                border-bottom: 2px solid #f0f0f0;
            }

            .header h1 {
                color: #e74c3c;
                margin-bottom: 10px;
                font-size: 2.2em;
                font-weight: 700;
            }

            .header p {
                color: #666;
                font-size: 1.1em;
            }

            .chat-container {
                flex: 1;
                overflow-y: auto;
                padding: 20px;
                margin-bottom: 20px;
                background: #f8f9fa;
                border-radius: 15px;
                border: 1px solid #e9ecef;
                min-height: 400px;
                scroll-behavior: smooth;
            }

            .message {
                margin-bottom: 20px;
                animation: fadeIn 0.3s ease-in;
            }

            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }

            .user-message {
                display: flex;
                justify-content: flex-end;
            }

            .user-message .message-content {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 12px 18px;
                border-radius: 20px 20px 5px 20px;
                max-width: 70%;
                word-wrap: break-word;
                box-shadow: 0 2px 10px rgba(102, 126, 234, 0.3);
            }

            .bot-message {
                display: flex;
                justify-content: flex-start;
            }

            .bot-message .message-content {
                background: white;
                color: #333;
                padding: 15px 20px;
                border-radius: 20px 20px 20px 5px;
                max-width: 80%;
                word-wrap: break-word;
                box-shadow: 0 2px 10px rgba(0,0,0,0.05);
                border: 1px solid #e9ecef;
            }

            .message-header {
                font-weight: 600;
                margin-bottom: 5px;
                font-size: 0.9em;
            }

            .user-message .message-header {
                color: rgba(255,255,255,0.9);
            }

            .bot-message .message-header {
                color: #e74c3c;
            }

            .input-section {
                display: flex;
                gap: 12px;
                align-items: flex-end;
                padding: 20px;
                background: white;
                border-radius: 15px;
                border: 1px solid #e9ecef;
                box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            }

            .input-wrapper {
                flex: 1;
                position: relative;
            }

            .input-wrapper textarea {
                width: 100%;
                padding: 12px 15px;
                border: 2px solid #e9ecef;
                border-radius: 12px;
                font-size: 16px;
                font-family: inherit;
                resize: none;
                min-height: 50px;
                max-height: 120px;
                transition: border-color 0.3s ease;
                background: #f8f9fa;
            }

            .input-wrapper textarea:focus {
                outline: none;
                border-color: #667eea;
                background: white;
            }

            .send-button {
                padding: 12px 24px;
                background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
                color: white;
                border: none;
                border-radius: 12px;
                cursor: pointer;
                font-size: 16px;
                font-weight: 600;
                transition: all 0.3s ease;
                min-width: 80px;
                height: 50px;
                display: flex;
                align-items: center;
                justify-content: center;
            }

            .send-button:hover:not(:disabled) {
                background: linear-gradient(135deg, #c0392b 0%, #a93226 100%);
                transform: translateY(-2px);
                box-shadow: 0 4px 15px rgba(231, 76, 60, 0.4);
            }

            .send-button:disabled {
                background: #bdc3c7;
                cursor: not-allowed;
                transform: none;
                box-shadow: none;
            }

            .sources {
                margin-top: 12px;
                padding-top: 12px;
                border-top: 1px solid #f0f0f0;
                font-size: 0.85em;
                color: #666;
            }

            .sources strong {
                color: #e74c3c;
            }

            .loading {
                display: flex;
                align-items: center;
                gap: 8px;
                color: #666;
                font-style: italic;
            }

            .loading-dots {
                display: flex;
                gap: 4px;
            }

            .loading-dot {
                width: 6px;
                height: 6px;
                border-radius: 50%;
                background: #667eea;
                animation: bounce 1.4s ease-in-out infinite both;
            }

            .loading-dot:nth-child(1) { animation-delay: -0.32s; }
            .loading-dot:nth-child(2) { animation-delay: -0.16s; }

            @keyframes bounce {
                0%, 80%, 100% { transform: scale(0); }
                40% { transform: scale(1); }
            }

            .status-indicator {
                position: absolute;
                top: 20px;
                right: 20px;
                width: 12px;
                height: 12px;
                border-radius: 50%;
                background: #27ae60;
                box-shadow: 0 0 10px rgba(39, 174, 96, 0.5);
            }

            .status-indicator.error {
                background: #e74c3c;
                box-shadow: 0 0 10px rgba(231, 76, 60, 0.5);
            }

            @media (max-width: 768px) {
                .container {
                    margin: 10px;
                    padding: 20px;
                    min-height: calc(100vh - 40px);
                }

                .header h1 {
                    font-size: 1.8em;
                }

                .user-message .message-content,
                .bot-message .message-content {
                    max-width: 90%;
                }

                .input-section {
                    flex-direction: column;
                    gap: 12px;
                }

                .send-button {
                    width: 100%;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="status-indicator" id="status-indicator"></div>

            <div class="header">
                <h1>Angel Assist</h1>
                <p>Need Help? Ask Angel anything about Angel One services, trading, or insurance policies!</p>
            </div>

            <div id="chat-container" class="chat-container">
                <div class="message bot-message">
                    <div class="message-content">
                        <div class="message-header">Angel Assist</div>
                        Hello! I'm here to help you with questions about Angel One services. How can I assist you today?
                    </div>
                </div>
            </div>

            <div class="input-section">
                <div class="input-wrapper">
                    <textarea 
                        id="question-input" 
                        placeholder="Type your question here..." 
                        maxlength="500"
                        rows="1"
                    ></textarea>
                </div>
                <button id="send-button" class="send-button" onclick="sendQuestion()">
                    Send
                </button>
            </div>
        </div>

        <script>
            const chatContainer = document.getElementById('chat-container');
            const questionInput = document.getElementById('question-input');
            const sendButton = document.getElementById('send-button');
            const statusIndicator = document.getElementById('status-indicator');

            // Auto-resize textarea
            questionInput.addEventListener('input', function() {
                this.style.height = 'auto';
                this.style.height = Math.min(this.scrollHeight, 120) + 'px';
            });

            // Handle Enter key (Shift+Enter for new line)
            questionInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    sendQuestion();
                }
            });

            // Check system health on load
            window.addEventListener('load', async () => {
                questionInput.focus();
                await checkHealth();
            });

            async function checkHealth() {
                try {
                    const response = await fetch('/health');
                    const data = await response.json();

                    if (data.status === 'healthy') {
                        statusIndicator.classList.remove('error');
                        statusIndicator.title = 'System is healthy';
                    } else {
                        statusIndicator.classList.add('error');
                        statusIndicator.title = 'System error: ' + (data.error || 'Unknown error');
                    }
                } catch (error) {
                    statusIndicator.classList.add('error');
                    statusIndicator.title = 'Cannot connect to server';
                }
            }

            async function sendQuestion() {
                const question = questionInput.value.trim();
                if (!question) return;

                // Disable input and button
                questionInput.disabled = true;
                sendButton.disabled = true;
                sendButton.innerHTML = '<div class="loading-dots"><div class="loading-dot"></div><div class="loading-dot"></div><div class="loading-dot"></div></div>';

                // Add user message
                addMessage(question, 'user');
                questionInput.value = '';
                questionInput.style.height = 'auto';

                // Add loading message
                const loadingId = addMessage('', 'bot', true);

                try {
                    const response = await fetch('/ask', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ question: question })
                    });

                    const data = await response.json();

                    // Remove loading message
                    document.getElementById(loadingId).remove();

                    if (response.ok) {
                        // Add bot response
                        let botMessage = data.answer;
                        if (data.sources && data.sources.length > 0) {
                            botMessage += '<div class="sources"><strong>Sources:</strong> ';
                            botMessage += data.sources.map(s => s.source).join(', ');
                            botMessage += '</div>';
                        }
                        addMessage(botMessage, 'bot');
                    } else {
                        addMessage('Sorry, I encountered an error. Please try again.', 'bot');
                    }
                } catch (error) {
                    // Remove loading message
                    const loadingElement = document.getElementById(loadingId);
                    if (loadingElement) loadingElement.remove();

                    addMessage('Sorry, I cannot connect to the server right now. Please try again later.', 'bot');
                }

                // Re-enable input and button
                questionInput.disabled = false;
                sendButton.disabled = false;
                sendButton.innerHTML = 'Send';
                questionInput.focus();
            }

            function addMessage(content, type, isLoading = false) {
                const messageDiv = document.createElement('div');
                const messageId = 'msg-' + Date.now() + '-' + Math.random();
                messageDiv.id = messageId;
                messageDiv.className = `message ${type}-message`;

                const messageContent = document.createElement('div');
                messageContent.className = 'message-content';

                if (isLoading) {
                    messageContent.innerHTML = `
                        <div class="message-header">Angel Assist</div>
                        <div class="loading">
                            <span>Thinking</span>
                            <div class="loading-dots">
                                <div class="loading-dot"></div>
                                <div class="loading-dot"></div>
                                <div class="loading-dot"></div>
                            </div>
                        </div>
                    `;
                } else {
                    const header = type === 'user' ? 'You' : 'Angel Assist';
                    messageContent.innerHTML = `
                        <div class="message-header">${header}</div>
                        <div>${content}</div>
                    `;
                }

                messageDiv.appendChild(messageContent);
                chatContainer.appendChild(messageDiv);
                chatContainer.scrollTop = chatContainer.scrollHeight;

                return messageId;
            }
        </script>
    </body>
    </html>
    """