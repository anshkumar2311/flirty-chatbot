import React, { useState, useRef, useEffect } from 'react';
import './App.css';

function App() {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState('checking');
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Check backend connection on component mount
    checkConnection();
  }, []);

  const checkConnection = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/status');
      if (response.ok) {
        setConnectionStatus('connected');
      } else {
        setConnectionStatus('disconnected');
      }
    } catch (error) {
      setConnectionStatus('disconnected');
      console.error('Backend connection error:', error);
    }
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = { text: inputMessage, sender: 'user', timestamp: new Date() };
    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:5000/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: inputMessage }),
      });

      if (!response.ok) {
        throw new Error('Network response was not ok');
      }

      const data = await response.json();
      const botMessage = {
        text: data.response,
        sender: 'bot',
        timestamp: new Date(),
        isTyping: false
      };
      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Error:', error);
      const errorMessage = {
        text: 'Sorry, I encountered an error. Please make sure Ollama is running with the dolphin3 model.',
        sender: 'bot',
        timestamp: new Date(),
        isError: true
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleClearChat = async () => {
    try {
      await fetch('http://localhost:5000/api/clear', {
        method: 'POST',
      });
      setMessages([]);
    } catch (error) {
      console.error('Error clearing chat:', error);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="App">
      <div className="chat-container">
        <div className="chat-header">
          <div className="header-content">
            <h1>Flirty Girlfriend Chat 💋</h1>
            <div className={`connection-status ${connectionStatus}`}>
              {connectionStatus === 'connected' ? 'Online' : 'Offline'}
            </div>
          </div>
          <button onClick={handleClearChat} className="clear-btn">
            Clear Chat
          </button>
        </div>

        <div className="messages-container">
          {messages.length === 0 ? (
            <div className="welcome-message">
              <div className="avatar">💋</div>
              <h2>Hey there, handsome! 😘</h2>
              <p>I've been waiting for you... Let's chat! 💕</p>
              <div className="hint">Pro tip: I love flirty, playful conversations!</div>
            </div>
          ) : (
            messages.map((message, index) => (
              <div key={index} className={`message ${message.sender}`}>
                <div className="message-content">
                  {message.text}
                  <div className="timestamp">{formatTime(message.timestamp)}</div>
                </div>
                {message.sender === 'bot' && (
                  <div className="avatar">💋</div>
                )}
              </div>
            ))
          )}
          {isLoading && (
            <div className="message bot">
              <div className="avatar">💋</div>
              <div className="message-content typing-indicator">
                <span>Typing</span>
                <div className="dots">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="input-container">
          <div className="input-wrapper">
            <textarea
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type your message here... (Press Enter to send)"
              disabled={isLoading || connectionStatus !== 'connected'}
              rows={1}
            />
            <button
              onClick={handleSendMessage}
              disabled={isLoading || !inputMessage.trim() || connectionStatus !== 'connected'}
              className="send-button"
            >
              Send
            </button>
          </div>
          {connectionStatus !== 'connected' && (
            <div className="connection-warning">
              ⚠️ Cannot connect to backend. Make sure Ollama is running with dolphin3 model.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
