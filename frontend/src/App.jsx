import { useState, useRef, useEffect } from 'react'
import './App.css'

function App() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const sendMessage = async () => {
    if (!input.trim() || loading) return

    const userMessage = { role: 'user', content: input, thinking: null }
    setMessages(prev => [...prev, userMessage])
    setInput('')
    setLoading(true)

    // Создаем временное сообщение для AI
    const tempMessageId = Date.now()
    setMessages(prev => [...prev, {
      id: tempMessageId,
      role: 'assistant',
      content: '',
      thinking: '',
    }])

    try {
      const response = await fetch('http://localhost:8000/chat/stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: input, model: 'llama3.2' }),
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6))
              
              setMessages(prev => prev.map(msg => {
                if (msg.id === tempMessageId) {
                  return {
                    ...msg,
                    content: msg.content + (data.content || ''),
                    thinking: msg.thinking + (data.thinking || ''),
                  }
                }
                return msg
              }))
            } catch (e) {
              console.error('Error parsing SSE data:', e)
            }
          }
        }
      }

      // Убираем временный ID после завершения
      setMessages(prev => prev.map(msg => {
        if (msg.id === tempMessageId) {
          const { id, ...rest } = msg
          return rest
        }
        return msg
      }))
    } catch (error) {
      console.error('Error:', error)
      setMessages(prev => prev.map(msg => {
        if (msg.id === tempMessageId) {
          return {
            role: 'assistant',
            content: 'Ошибка при отправке запроса. Убедитесь, что бэкенд запущен и Ollama работает.',
            thinking: null,
          }
        }
        return msg
      }))
    } finally {
      setLoading(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  return (
    <div className="app">
      <div className="chat-container">
        <div className="chat-header">
          <h1>Ollama Chat</h1>
        </div>
        
        <div className="messages">
          {messages.length === 0 && (
            <div className="empty-state">
              <p>Начните диалог с AI</p>
            </div>
          )}
          
          {messages.map((msg, idx) => (
            <div key={msg.id || idx} className={`message ${msg.role}`}>
              <div className="message-header">
                {msg.role === 'user' ? '👤 Вы' : '🤖 AI'}
              </div>
              
              {msg.thinking && msg.thinking.trim() && (
                <div className="thinking">
                  <div className="thinking-label">💭 Мышление:</div>
                  <div className="thinking-content">{msg.thinking}</div>
                </div>
              )}
              
              {msg.content && (
                <div className="message-content">{msg.content}</div>
              )}
              
              {!msg.content && msg.role === 'assistant' && loading && (
                <div className="message-content">
                  <span className="typing-indicator">Печатает...</span>
                </div>
              )}
            </div>
          ))}
          
          <div ref={messagesEndRef} />
        </div>
        
        <div className="input-container">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Введите сообщение..."
            rows={1}
            disabled={loading}
          />
          <button 
            onClick={sendMessage} 
            disabled={loading || !input.trim()}
            className="send-button"
          >
            Отправить
          </button>
        </div>
      </div>
    </div>
  )
}

export default App
