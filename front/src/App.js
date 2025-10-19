import React, { useState, useEffect, useRef, useCallback } from 'react';
import './App.css';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function App() {
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');

  const fetchMessages = useCallback(async () => {
    const response = await fetch(`${API_BASE_URL}/messages`);
    const data = await response.json();
    setMessages(data);
    return data;
  }, []);

  const sendMessage = async () => {
    if (!newMessage.trim()) return;

    const response = await fetch(`${API_BASE_URL}/messages`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        content: newMessage,
        role: 'user',
      }),
    });
    const data = await response.json();

    setNewMessage('');
  };

  const clearMessages = async () => {
    await fetch(`${API_BASE_URL}/messages`, {
      method: 'DELETE',
    });
    fetchMessages();
  };


  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      sendMessage();
    }
  };

  useEffect(() => {
    fetchMessages();

    const interval = setInterval(() => {
      fetchMessages();
    }, 5000);

    return () => clearInterval(interval);
  }, [fetchMessages]);

  return (
    <div className="App">
      <header className="App-header">
        <h1>Bobchat</h1>
      </header>

      <div className="chat-container">
        <div className="chat-area">
          <div className="messages">
            {messages.map((message) => (
              <div key={message.id} className="message-block">
                <div className="message-header">
                  <span className="participant">{message.role}</span>
                  <span className="timestamp">{new Date(message.timestamp).toLocaleTimeString()}</span>
                </div>
                <div className="message-content">{message.content}</div>
              </div>
            ))}
          </div>
          <div className="message-input">
            <input
              type="text"
              placeholder="Type a message..."
              value={newMessage}
              onChange={(e) => setNewMessage(e.target.value)}
              onKeyPress={handleKeyPress}
            />
            <button onClick={sendMessage}>Send</button>
            <button onClick={clearMessages} style={{ marginLeft: '10px', backgroundColor: '#dc3545', color: 'white' }}>Clear</button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;