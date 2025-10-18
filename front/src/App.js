import React, { useState, useEffect, useRef } from 'react';
import './App.css';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function App() {
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [username, setUsername] = useState('');
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
    if (!newMessage.trim() || !username.trim()) return;

    const response = await fetch(`${API_BASE_URL}/messages`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        content: newMessage,
        participant_name: username,
      }),
    });
    const data = await response.json();
    setMessages(prev => [...prev, data]);
    setNewMessage('');

    setIsPolling(true);
    lastMessageCountRef.current = messages.length + 1;
  };

  const startPolling = () => {
    if (pollingRef.current) return;

    pollingRef.current = setInterval(async () => {
      const currentMessages = await fetchMessages();
      if (currentMessages.length > lastMessageCountRef.current) {
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
        <h1>Chat App</h1>
        {!username && (
          <div>
            <input
              type="text"
              placeholder="Enter your username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && username.trim() && setUsername(username.trim())}
            />
          </div>
        )}
      </header>

      <div className="chat-container">
        <div className="chat-area">
          <div className="chat-header">
            <h3>General Chat</h3>
          </div>
          <div className="messages">
            {messages.map((message) => (
              <div key={message.id} className="message-block">
                <div className="message-header">
                  <span className="participant">{message.participant_name}</span>
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
              onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
            />
            <button onClick={sendMessage}>Send</button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;