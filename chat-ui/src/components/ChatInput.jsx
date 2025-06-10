import { useState, useRef, useEffect } from 'react';

const ChatInput = ({ onSend }) => {
  const [input, setInput] = useState('');
  const [protocols, setProtocols] = useState('');
  const textareaRef = useRef(null);

  const handleSend = () => {
    const trimmedInput = input.trim();
    const trimmedProtocols = protocols.trim();
    if (!trimmedInput || !trimmedProtocols) return;

    const protocolList = trimmedProtocols
      .split(',')
      .map(p => p.trim())
      .filter(p => p.length > 0);

    if (protocolList.length === 0) return;

    onSend(trimmedInput, protocolList);
    setInput('');
    setProtocols('');
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  // Auto-grow height as input changes
  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = `${textarea.scrollHeight}px`;
    }
  }, [input]);

  return (
    <div className="d-flex flex-column gap-2">
      <textarea
        ref={textareaRef}
        className="form-control"
        placeholder="Describe your property..."
        rows="1"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={handleKeyDown}
        style={{ overflow: 'hidden', resize: 'none' }}
      />
      <input
        type="text"
        className="form-control"
        placeholder="Enter protocols (comma-separated)"
        value={protocols}
        onChange={(e) => setProtocols(e.target.value)}
      />
      <div className="d-flex justify-content-end">
      <button className="btn btn-outline-primary" onClick={handleSend}>
        Send
      </button>
      </div>
    </div>
  );
};

export default ChatInput;