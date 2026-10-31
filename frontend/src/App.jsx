import { useEffect, useMemo, useRef, useState } from 'react';

const API_BASE =
  import.meta.env.VITE_API_BASE ||
  (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:8010'
    : window.location.origin);
const ACCEPTED_TYPES = ['.pdf', '.docx', '.pptx'];

function App() {
  const [sessionId] = useState(() => crypto.randomUUID());
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [question, setQuestion] = useState('');
  const [topic, setTopic] = useState('');
  const [flashMessage, setFlashMessage] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const [isSending, setIsSending] = useState(false);
  const [isChatOpen, setIsChatOpen] = useState(true);
  const [isChatFullscreen, setIsChatFullscreen] = useState(false);
  const [chatMessages, setChatMessages] = useState([
    {
      sender: 'assistant',
      text: 'Upload your lecture materials to begin. Only PDF, DOCX, and PPTX files are accepted.',
    },
  ]);
  const messagesListRef = useRef(null);

  const acceptedFileText = useMemo(
    () => ACCEPTED_TYPES.map((type) => type.toUpperCase().replace('.', '')).join(', '),
    [],
  );

  useEffect(() => {
    const container = messagesListRef.current;
    if (!container) return;
    container.scrollTo({ top: container.scrollHeight, behavior: 'smooth' });
  }, [chatMessages, isChatOpen]);

  const addMessage = (sender, text) => {
    setChatMessages((current) => [...current, { sender, text }]);
  };

  const handleFileSelection = (event) => {
    const files = Array.from(event.target.files || []);
    const invalid = files.filter((file) => {
      const ext = file.name.toLowerCase().substring(file.name.lastIndexOf('.'));
      return !ACCEPTED_TYPES.includes(ext);
    });

    if (invalid.length) {
      setFlashMessage('Only PDF, DOCX, and PPTX files are allowed.');
      event.target.value = '';
      return;
    }

    setSelectedFiles(files);
    setFlashMessage('');
  };

  const handleUpload = async () => {
    if (!selectedFiles.length) {
      setFlashMessage('Select at least one file to upload.');
      return;
    }

    setIsUploading(true);
    setFlashMessage('');

    try {
      const formData = new FormData();
      formData.append('session_id', sessionId);
      selectedFiles.forEach((file) => formData.append('files', file));

      const response = await fetch(`${API_BASE}/api/upload`, {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || 'Upload failed.');
      }

      setUploadedFiles(data.files);
      setSelectedFiles([]);
      setIsChatOpen(true);
      addMessage(
        'assistant',
        `Uploaded ${data.files.length} lecture file(s). You can start asking questions based only on these materials.`,
      );
    } catch (error) {
      setFlashMessage(error.message || 'Something went wrong during upload.');
    } finally {
      setIsUploading(false);
    }
  };

  const handleQuestionSubmit = async (event) => {
    event.preventDefault();
    const trimmed = question.trim();
    if (!trimmed) {
      setFlashMessage('Please enter a question.');
      return;
    }
    if (!uploadedFiles.length) {
      setFlashMessage('Upload files before asking questions.');
      return;
    }

    setIsSending(true);
    setFlashMessage('');
    addMessage('user', trimmed);
    setQuestion('');

    try {
      const response = await fetch(`${API_BASE}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sessionId, question: trimmed }),
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || 'Question failed.');
      }

      addMessage('assistant', data.answer);
    } catch (error) {
      setFlashMessage(error.message || 'Unable to answer that question.');
    } finally {
      setIsSending(false);
    }
  };

  const handleTopicSubmit = async (event) => {
    event.preventDefault();
    const trimmed = topic.trim();
    if (!trimmed) {
      setFlashMessage('Please enter a study topic.');
      return;
    }
    if (!uploadedFiles.length) {
      setFlashMessage('Upload files before generating study questions.');
      return;
    }

    setIsSending(true);
    setFlashMessage('');

    try {
      const response = await fetch(`${API_BASE}/api/test-questions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sessionId, topic: trimmed }),
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || 'Unable to generate questions.');
      }

      addMessage('assistant', data.questions);
      setTopic('');
    } catch (error) {
      setFlashMessage(error.message || 'Unable to generate questions.');
    } finally {
      setIsSending(false);
    }
  };

  return (
    <div className="app-shell">
      <div className="app-card">
        <header className="page-header">
          <div>
            <p className="eyebrow">Study assistant</p>
            <h1>TingeStudies</h1>
          </div>
        </header>

        <section className="upload-panel">
          <label className="label">Upload course materials</label>
          <div className="upload-row">
            <input
              type="file"
              accept=".pdf,.docx,.pptx"
              multiple
              onChange={handleFileSelection}
            />
            <button type="button" onClick={handleUpload} disabled={isUploading || !selectedFiles.length}>
              {isUploading ? 'Uploading...' : 'Upload files'}
            </button>
          </div>
          <p className="small-print">Accepted formats: {acceptedFileText}</p>
          {selectedFiles.length > 0 && (
            <div className="selected-files">
              {selectedFiles.map((file) => (
                <span key={file.name}>{file.name}</span>
              ))}
            </div>
          )}
          {uploadedFiles.length > 0 && (
            <div className="uploaded-files">
              <strong>Uploaded:</strong>
              {uploadedFiles.map((file) => (
                <span key={file}>{file}</span>
              ))}
            </div>
          )}
          {flashMessage && <p className="flash-message">{flashMessage}</p>}
        </section>

        {uploadedFiles.length > 0 && (
          <>
            <section className={`chat-panel ${isChatFullscreen ? 'fullscreen' : ''} ${isChatOpen ? '' : 'collapsed'}`}>
              <div className="chat-header">
                <h2>Study chat</h2>
                <div className="chat-actions">
                  <button type="button" className="secondary-button" onClick={() => setIsChatOpen((open) => !open)}>
                    {isChatOpen ? 'Hide chat' : 'Show chat'}
                  </button>
                  <button type="button" className="secondary-button" onClick={() => setIsChatFullscreen((value) => !value)}>
                    {isChatFullscreen ? 'Exit full screen' : 'Full screen'}
                  </button>
                </div>
              </div>

              {isChatOpen && (
                <>
                  <div className="messages" ref={messagesListRef} aria-live="polite">
                    {chatMessages.map((message, index) => (
                      <div key={`${message.sender}-${index}`} className={`message ${message.sender}`}>
                        <span>{message.sender === 'assistant' ? 'AI tutor' : 'You'}</span>
                        <p>{message.text}</p>
                      </div>
                    ))}
                  </div>

                  <form onSubmit={handleQuestionSubmit} className="chat-composer">
                    <textarea
                      value={question}
                      onChange={(event) => setQuestion(event.target.value)}
                      placeholder="Ask about your uploaded lecture materials..."
                      rows="3"
                    />
                    <div className="composer-actions">
                      <button type="submit" disabled={isSending}>
                        {isSending ? 'Sending...' : 'Ask'}
                      </button>
                    </div>
                  </form>
                </>
              )}
            </section>

            <div className="study-panel">
              <form onSubmit={handleTopicSubmit} className="prompt-box">
                <label className="label">Study tips</label>
                <input
                  type="text"
                  value={topic}
                  onChange={(event) => setTopic(event.target.value)}
                  placeholder="Topic you need help with"
                />
                <button type="submit" disabled={isSending}>
                  {isSending ? 'Generating...' : 'Generate study tips'}
                </button>
              </form>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

export default App;
