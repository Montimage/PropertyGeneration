import { useState, useEffect, useRef } from 'react';
import ChatBubble from './components/ChatBubble';
import ChatInput from './components/ChatInput';

function App() {
  const [messages, setMessages] = useState([]);
  const bottomRef = useRef(null);

  const sendMessage = async (text, protocols) => {
    // Add user message
    setMessages((prev) => [...prev, {
      type: "text",
      role: "user",
      content: text
    }]);

    // Show temporary "thinking..." message
    const thinkingMessage = {
      type: "system",
      role: "ai",
      content: "Thinking..."
    };
    setMessages((prev) => [...prev, thinkingMessage]);

    try {
      const response = await fetch('http://localhost:8000/generate-property', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ input_text: text, protocol_list: protocols }),
      });

      const data = await response.json();
      console.log("Raw response from backend:", data);
      console.log("Type:", data.type, "status:", data.status);

      // Replace "thinking..." with the actual AI message
      setMessages((prev) => prev.slice(0, -1).concat(data));
    } catch (error) {
      setMessages((prev) =>
        prev.slice(0, -1).concat({
          type: 'error',
          role: 'system',
          content: 'Error contacting backend.'
        })
      );
    }
};

  // Auto-scroll to bottom when messages update
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const renderMessage = (msg, idx) => {
    if (msg.type === 'property') {
      return (
      <ChatBubble
        key={idx}
        sender={msg.role}
        text={msg.content}
        editable={msg.editable ?? false} 
        askToSave={msg.ask_to_save ?? false}
        validationFeedback={msg.validation_feedback ?? null}
        status={msg.status ?? null}
      />
    );
    } else if (msg.type === 'question'){
      return <ChatBubble key={idx} sender={msg.role} text={msg.content} isQuestion />;
    } else if (msg.type === 'error') {
      return <ChatBubble key={idx} sender={msg.role} text={msg.content} isError />;
    } else {
      return <ChatBubble key={idx} sender={msg.role} text={msg.content} />;
    }
  };

  return (
    <div className="d-flex justify-content-center align-items-center vh-100 bg-light">
      <div className="container px-3">
        <div className="d-flex flex-column bg-white border rounded shadow-sm p-4" style={{ maxHeight: '90vh', height: '100%' }}>
          <h4 className="text-center mb-4 text-secondary">Chat Property Generator</h4>

          <div className="flex-grow-1 overflow-auto mb-3 px-1" id="chat-window">
            {messages.map((msg, idx) => renderMessage(msg, idx))}
            <div ref={bottomRef}></div>
          </div>
          <ChatInput onSend={sendMessage} />
        </div>
      </div>
    </div>
  );
}

export default App;