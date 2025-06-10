import React, { useState, useEffect } from 'react';

const ChatBubble = ({ 
  sender, 
  text, // Content of the message
  editable = false,
  askToSave = false,
  validationFeedback = null,
  isQuestion = false,
  isError = false,
  status = null
}) => {
  const isUser = sender === 'user';
  const [editedText, setEditedText] = useState(text);

  // Save property form
  const [showForm, setShowForm] = useState(false);
  const [description, setDescription] = useState('');
  const [protocols, setProtocols] = useState('');
  const [fileName, setFileName] = useState('');
  const [submitStatus, setSubmitStatus] = useState(null); // 'sucess' | 'error' | null

  useEffect(() => {
    setEditedText(text);
  }, [text]);

  const handleEditChange = (e) => {
    const newText = e.target.value;
    setEditedText(newText);
  };

  const handleYesClick = () => setShowForm(true);
  const handleNoClick = () => setShowForm(false);

  const handleSubmit = async () => {
    const payload = {
      description: description,
      protocol: protocols
      .split(',')
      .map(p => p.trim())
      .filter(p => p.length > 0),
      name: fileName,
      content: editedText,
    };

    try {
      const response = await fetch('http://localhost:8000/save-property', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok){
        throw new Error('Failed to save property');
      }
      await response.json();
      setSubmitStatus('success');
    } catch (error) {
      console.error('Error saving property:', error);
      setSubmitStatus('error');
    }
  };

  return (
    <div className={`d-flex ${isUser ? 'justify-content-end' : 'justify-content-start'} mb-2`}>
      <div
        className={`p-3 rounded-3 shadow-sm w-100 ${isUser ? 'bg-success text-white' : 'bg-white border'}`}
        style={{ maxWidth: '80%' }}
      >
        {isQuestion && <strong className="d-block mb-2">The assistant needs more info:</strong>}

        {isError && (
          <strong className="d-block mb-2 text-danger">An error has occurred:</strong>
        )}
        {editable && status === 'valid' && (
          <strong className="d-block mb-2">A valid property was generated:</strong>
        )}

        {editable && status === 'invalid' && (
          <strong className="d-block mb-2">An invalid property was generated. This is the last attempt of the AI at generating a property:</strong>
        )}

        {editable ? (
          <textarea
            className="form-control mb-2"
            rows={6}
            value={editedText}
            onChange={handleEditChange}
            style={{ fontFamily: 'monospace', whiteSpace: 'pre-wrap' }}
          />
        ) : (
          <pre className="mb-0" style={{ fontFamily: 'inherit', whiteSpace: 'pre-wrap' }}>
            {text}
          </pre>
        )}
        {status === 'invalid' && validationFeedback && (
          <div className="mt-2">
            <div className="fw-semibold mb-1">The system has provided the following validation feedback:</div>
            <pre className="mb-0" style={{ whiteSpace: 'pre-wrap', fontFamily: 'inherit' }}>
              {validationFeedback}
            </pre>
          </div>
        )}

        {askToSave && (
          <div className="mt-3">
            <div className="mb-2 text-muted">
              Would you like to save it in the database?
            </div>
            <div className="d-flex gap-2 mb-3">
              <button className="btn btn-sm btn-outline-success" onClick={handleYesClick}>Yes</button>
              <button className="btn btn-sm btn-outline-secondary" onClick={handleNoClick}>No</button>
            </div>

            {showForm && (
              <div className="border-top pt-3">
                <div className="mb-2">
                  <label className="form-label">Short Description</label>
                  <input
                    type="text"
                    className="form-control"
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                  />
                </div>

                <div className="mb-2">
                  <label className="form-label">Protocols (comma-separated)</label>
                  <input
                    type="text"
                    className="form-control"
                    value={protocols}
                    onChange={(e) => setProtocols(e.target.value)}
                  />
                </div>

                <div className="mb-2">
                  <label className="form-label">File Name</label>
                  <input
                    type="text"
                    className="form-control"
                    value={fileName}
                    onChange={(e) => setFileName(e.target.value)}
                  />
                </div>

                <div className="text-end">
                  <button className="btn btn-primary btn-sm" onClick={handleSubmit}>
                    Submit
                  </button>
                </div>
                {submitStatus === 'success' && (
                  <div className="text-success mt-2">Property saved successfully.</div>
                )}
                {submitStatus === 'error' && (
                  <div className="text-danger mt-2">There was an error saving the property.</div>
                )}
                
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default ChatBubble;