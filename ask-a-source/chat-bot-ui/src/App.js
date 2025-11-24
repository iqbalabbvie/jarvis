import React, { useState } from 'react';
import axios from 'axios';
import './App.css'; 
import Loader from './Loader';
 
function App() {
  const [message, setMessage] = useState('');
  const [conversation, setConversation] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [openBladeIndex, setOpenBladeIndex] = useState(null);
  const [isConfigOpen, setIsConfigOpen] = useState(false);
  const [userPrefersnce, setUserPreferance] = useState('');
  const [admpComponent, setAdmpComponent] = useState('accordian');
 
  const handleSend = () => {
    if (message.trim() === '') return; 
 
    setLoading(true);
 
    // Post the message to the Flask backend
    axios.post('http://jarvis-api-app.aws-k8s-d/api/post-data', { message })
      .then(response => {
        let regex = /\[.*?\]/g;
        let responseText = response.data.content.replace(regex, '');
        let references = `File Name : ${response.data.references[0].filename}\n Content :\n${response.data.references[0].text}` ;
        setConversation(prev => [...prev, { user: 'You', text: message}, { user: 'Server', text: responseText, reference: references}]);
        setMessage('');
        setLoading(false);
      })
      .catch(error => {
        let errorText = error.message +'. Unable to fetch the response for the request';
        setConversation(prev => [...prev, { user: 'You', text: message}, { user: 'Server', text: '', errorText: errorText}]);
        setMessage('');
        setLoading(false);
      });
  };
 
  const handleUserPreferanceUpdate = (e) => {
    setUserPreferance(e.target.value);
  };
  
  const handleAdmpComponentUpdate = (e) => {
    setAdmpComponent(e.target.value);
  };

  const handleToggleBlade = (index) => {
    setOpenBladeIndex(openBladeIndex === index ? null : index);
  };

  const toggleConfig = () => {
    setIsConfigOpen(!isConfigOpen);
  };

  return (
    <div className="App">
      <div class="header">
        <img src= '/header-logo.png' alt = "Logo" className='header-logo' />
        <h1 className="header-text">Knowledge Chatbot</h1>
        <button onClick={toggleConfig} className='config-toggle-btn'>
          &#x2699;
        </button>
      </div>
      <div className={`chat-container ${isConfigOpen ? 'config-open' : ''}`}>
      <div className="chat-box">
        <div className="messages">
        {conversation.map((msg, index) => (
          <div key={index} className={`message ${msg.user === 'You' ? 'user' : 'Server'}`}>
            <img 
                src={msg.user === 'You' ? '/user-logo.png' : '/bot-logo.png'}
                alt={msg.user === 'You' ? 'User' : 'bot'}
                className='message-logo'
            />
            <div className='message-content'>
              <div className = {`${msg.text ? 'responseText' : 'errorText'}`}>{msg.text || msg.errorText}</div>
              {msg.user === 'Server' && msg.reference && (
                <>
                <a
                  href = '#'
                  className='reference-link'
                  onClick={(e) =>{
                    e.preventDefault();
                    handleToggleBlade(index);
                  }}
                  >
                      {openBladeIndex === index ? '[-] Collapse' : '[+]Expand Reference'}
                  </a>
                  <div className= {`blade ${openBladeIndex === index ? 'open' : 'closed'}`}
                    dangerouslySetInnerHTML = {{__html: msg.reference.replace(/\n /g, '<br / > ') }}>  
                  </div>
                </>
                
              )}
            </div>
            {error && <div className="error">Error: {error.message}</div>}
          </div>
        ))} 
        {loading && (
          <div className='messages loader'>
            <Loader/>
          </div>
        )}
        </div>
        <div className="input-box">
        <input
                    type="text"
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    placeholder="Type your message..."
                  />
        <button onClick={handleSend} disabled={loading}>
                    {loading ? 'Sending...' : 'Send'}
        </button>
        </div>
      </div>
      {isConfigOpen && (
        <div className='config-box'>
          <div className='config-header'>
              <span>Settings</span>
          </div>
          <div className='admp-component-list'>
            <span class="admp-component-list-title">ADMP Component List</span>
            <select value = {admpComponent} onChange={handleAdmpComponentUpdate} >
              <option value="accordian">Accordian</option>
              <option value="rangeSlider">Range Slider</option>
              <option value="icon">Icons</option>
              <option value="Action">Action</option>
            </select>
          </div>
          <div className='user-preferance'>
            <span class="user-preferance-title">User Preferance</span>
            <label>
              <input type="radio" name="Developer" value="developer" onChange={handleUserPreferanceUpdate} checked={userPrefersnce === "developer"} />
              Developer
            </label>
            <label>
              <input type="radio" name="Business" value="business" onChange={handleUserPreferanceUpdate}  checked={userPrefersnce === "business"} />
              Business
            </label>
          </div>
          <button className="save-config-btn">Save</button>
          <button onClick={toggleConfig} className="close-config-btn">Close</button>

        </div>

      )}
      </div>     
    </div>
);
}
 
export default App;