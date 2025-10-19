import React, { useState, useEffect, useRef } from 'react';
import './App.css';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function App() {
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [isPolling, setIsPolling] = useState(false);
  const pollingRef = useRef(null);
  const lastMessageCountRef = useRef(0);

  const fetchMessages = async () => {
    const response = await fetch(`${API_BASE_URL}/messages`);
    const data = await response.json();
    setMessages(data);
    return data;
  };

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

    lastMessageCountRef.current = messages.length + 1;
    setMessages(prev => [...prev, data]);
    setNewMessage('');

    setIsPolling(true);
  };

  const startPolling = () => {
    if (pollingRef.current) return;

    console.log('Starting polling for new messages...');
    pollingRef.current = setInterval(async () => {
      console.log('Polling for messages...');
      const currentMessages = await fetchMessages();
      console.log(`Current messages: ${currentMessages.length}, Expected: ${lastMessageCountRef.current}`);
      if (currentMessages.length > lastMessageCountRef.current) {
        console.log('New message detected, stopping polling');
        setIsPolling(false);
        clearInterval(pollingRef.current);
        pollingRef.current = null;
      }
    }, 5000);
  };

  const stopPolling = () => {
    if (pollingRef.current) {
      clearInterval(pollingRef.current);
      pollingRef.current = null;
    }
    setIsPolling(false);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      sendMessage();
    }
  };

  useEffect(() => {
    fetchMessages();
  }, []);

  useEffect(() => {
    if (isPolling) {
      startPolling();
    } else {
      stopPolling();
    }

    return () => stopPolling();
  }, [isPolling]);

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
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;