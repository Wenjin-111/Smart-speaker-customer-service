<template>
  <div class="app" :data-theme="theme">
    <div class="main-layout">
      <aside class="sidebar" :class="{ 'sidebar-hidden': !showSidebar }">
        <div class="sidebar-content">
          <div class="sidebar-header">
            <h3>对话历史</h3>
            <button class="new-chat-btn" @click="createNewChat">+ 新对话</button>
          </div>
          <div class="sessions-list">
            <div v-for="session in sessions" :key="session.id" class="session-item" :class="{ active: currentSessionId === session.id }" @click="switchSession(session.id)">
              <div class="session-info">
                <div class="session-title">{{ session.title }}</div>
                <div class="session-time">{{ formatTime(session.updatedAt) }}</div>
              </div>
              <button class="delete-session" @click.stop="deleteSession(session.id)">×</button>
            </div>
          </div>
        </div>
      </aside>
      <div class="main-content">
        <header class="header">
          <div class="header-content">
            <div class="header-left">
              <button class="sidebar-toggle" @click="toggleSidebar">☰</button>
              <h1 class="title">🐱 智能音箱客服</h1>
            </div>
            <button class="theme-toggle" @click="toggleTheme">{{ theme === 'light' ? '🌙' : '☀️' }}</button>
          </div>
        </header>
        <main class="chat-container">
          <div class="messages" ref="messagesContainer">
            <div v-for="(message, index) in currentMessages" :key="`${currentSessionId}-${index}`" class="message-wrapper" :class="{ 'user-message': message.role === 'user', 'assistant-message': message.role === 'assistant' }">
              <div class="message" :class="message.role">
                <div class="avatar">
                  <span v-if="message.role === 'user'">😊</span>
                  <span v-else>🐱</span>
                </div>
                <div class="content">
                  <div class="message-content" v-html="formatMessage(message.content)"></div>
                  <div v-if="message.role === 'assistant' && message.isThinking" class="thinking-indicator">
                    <div class="thinking-dots">
                      <span></span>
                      <span></span>
                      <span></span>
                    </div>
                    <span class="thinking-text">客服正在思考...</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="input-area">
            <div class="input-container">
              <textarea v-model="userInput" @keydown="handleKeyDown" placeholder="请输入您的问题..." rows="1" ref="textareaRef"></textarea>
              <button @click="sendMessage" :disabled="!userInput.trim() || isLoading" class="send-btn">{{ isLoading ? '...' : '发送' }}</button>
            </div>
          </div>
        </main>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick, watch, computed } from 'vue'

const theme = ref('light')
const showSidebar = ref(true)
const sessions = reactive([])
const currentSessionId = ref(null)
const userInput = ref('')
const isLoading = ref(false)
const messagesContainer = ref(null)
const textareaRef = ref(null)

const currentMessages = computed(() => {
  const session = sessions.find(s => s.id === currentSessionId.value)
  return session ? session.messages : []
})

const generateId = () => {
  return Date.now().toString(36) + Math.random().toString(36).substr(2)
}

const getSessionTitle = (messages) => {
  if (messages.length === 0) return '新对话'
  const firstUserMsg = messages.find(m => m.role === 'user')
  if (firstUserMsg) {
    const content = firstUserMsg.content
    return content.length > 20 ? content.substring(0, 20) + '...' : content
  }
  return '新对话'
}

const saveSessions = () => {
  localStorage.setItem('chat_sessions', JSON.stringify(sessions))
}

const loadSessions = () => {
  const stored = localStorage.getItem('chat_sessions')
  if (stored) {
    const loadedSessions = JSON.parse(stored)
    sessions.splice(0, sessions.length, ...loadedSessions)
    currentSessionId.value = sessions[0]?.id || null
  } else {
    createNewChat()
  }
}

onMounted(() => {
  const savedTheme = localStorage.getItem('theme')
  if (savedTheme) {
    theme.value = savedTheme
    document.documentElement.setAttribute('data-theme', savedTheme)
  }
  loadSessions()
})

const toggleTheme = () => {
  theme.value = theme.value === 'light' ? 'dark' : 'light'
  document.documentElement.setAttribute('data-theme', theme.value)
  localStorage.setItem('theme', theme.value)
}

const toggleSidebar = () => {
  showSidebar.value = !showSidebar.value
}

const createNewChat = () => {
  const newId = generateId()
  const newSession = {
    id: newId,
    title: '新对话',
    messages: [{
      role: 'assistant',
      content: '你好，我是智能音箱客服，请问你有什么需要咨询的问题',
      isThinking: false
    }],
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  }
  sessions.unshift(newSession)
  currentSessionId.value = newId
  saveSessions()
}

const switchSession = (sessionId) => {
  currentSessionId.value = sessionId
  userInput.value = ''
  nextTick(() => {
    scrollToBottom()
  })
}

const deleteSession = (sessionId) => {
  if (sessions.length === 1) {
    createNewChat()
  }
  const index = sessions.findIndex(s => s.id === sessionId)
  if (index !== -1) {
    sessions.splice(index, 1)
    if (currentSessionId.value === sessionId) {
      currentSessionId.value = sessions[0]?.id || null
    }
    saveSessions()
  }
}

const formatTime = (timestamp) => {
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now - date
  if (diff < 24 * 60 * 60 * 1000) {
    return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  } else if (diff < 7 * 24 * 60 * 60 * 1000) {
    const days = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
    return days[date.getDay()]
  } else {
    return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
  }
}

watch(userInput, () => {
  nextTick(() => {
    const textarea = textareaRef.value
    if (textarea) {
      textarea.style.height = 'auto'
      textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px'
    }
  })
})

const sendMessage = async () => {
  if (!userInput.value.trim() || isLoading.value || !currentSessionId.value) return

  const messageText = userInput.value.trim()
  userInput.value = ''

  const session = sessions.find(s => s.id === currentSessionId.value)
  if (!session) return

  session.messages.push({
    role: 'user',
    content: messageText
  })

  const assistantMessageIndex = session.messages.length
  session.messages.push({
    role: 'assistant',
    content: '',
    isThinking: true
  })

  session.title = getSessionTitle(session.messages)
  session.updatedAt = new Date().toISOString()
  saveSessions()

  isLoading.value = true
  scrollToBottom()

  try {
    const response = await fetch('/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        messages: session.messages.slice(0, -1).map(msg => ({
          role: msg.role,
          content: msg.content
        }))
      })
    })

    if (!response.ok) throw new Error(`HTTP ${response.status}`)

    const reader = response.body.getReader()
    const decoder = new TextDecoder('utf-8')
    let accumulated = ''

    session.messages[assistantMessageIndex].isThinking = false

    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      const chunk = decoder.decode(value, { stream: true })
      accumulated += chunk
      session.messages[assistantMessageIndex].content = accumulated
      scrollToBottom()
    }

    session.updatedAt = new Date().toISOString()
    saveSessions()

  } catch (error) {
    console.error('请求失败:', error)
    session.messages[assistantMessageIndex].content = '抱歉，发生错误，请稍后重试。'
    session.messages[assistantMessageIndex].isThinking = false
    session.updatedAt = new Date().toISOString()
    saveSessions()
  } finally {
    isLoading.value = false
    scrollToBottom()
  }
}

const handleKeyDown = (event) => {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    sendMessage()
  }
}

const scrollToBottom = () => {
  nextTick(() => {
    const container = messagesContainer.value
    if (container) {
      container.scrollTop = container.scrollHeight
    }
  })
}

const renderMarkdown = (text) => {
  if (!text) return ''
  let html = text
  html = html.replace(/[&<>"]/g, (char) => {
    const map = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }
    return map[char]
  })
  html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
  html = html.replace(/\*([^*]+)\*/g, '<em>$1</em>')
  html = html.replace(/^### (.+)$/gm, '<h3>$1</h3>')
  html = html.replace(/^## (.+)$/gm, '<h2>$1</h2>')
  html = html.replace(/^# (.+)$/gm, '<h1>$1</h1>')
  html = html.replace(/^- (.+)$/gm, '<li>$1</li>')
  html = html.replace(/^\d+\. (.+)$/gm, '<li>$1</li>')
  const paragraphs = html.split(/\n\n+/)
  html = paragraphs.map(paragraph => {
    if (paragraph.includes('<h') || paragraph.includes('<li>') || paragraph.includes('<ul>')) {
      paragraph = paragraph.replace(/\n/g, '<br>')
      return paragraph
    }
    paragraph = paragraph.replace(/\n/g, '<br>')
    return `<p>${paragraph}</p>`
  }).join('\n')
  html = html.replace(/(<li>.*?<\/li>)/gs, '<ul>$1</ul>')
  return html
}

const formatMessage = (content) => {
  return renderMarkdown(content)
}
</script>

<style scoped>
.app { height: 100vh; background: var(--bg-primary); position: relative; overflow: hidden; }
.main-layout { display: flex; height: 100vh; }
.sidebar { width: 280px; background: var(--bg-secondary); border-right: 1px solid var(--border-color); display: flex; flex-direction: column; transition: transform 0.3s ease; z-index: 20; }
.sidebar-hidden { transform: translateX(-100%); }
.sidebar-content { padding: 1.5rem; height: 100%; display: flex; flex-direction: column; }
.sidebar-header h3 { margin: 0 0 1rem 0; color: var(--text-primary); font-size: 1.2rem; }
.new-chat-btn { width: 100%; padding: 0.75rem; background: var(--accent-color); color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 0.9rem; transition: all 0.3s ease; margin-bottom: 1rem; }
.new-chat-btn:hover { background: var(--accent-hover); transform: translateY(-1px); }
.sessions-list { flex: 1; overflow-y: auto; }
.session-item { display: flex; align-items: center; padding: 0.75rem; cursor: pointer; transition: all 0.2s ease; border-radius: 6px; margin-bottom: 0.25rem; }
.session-item:hover { background: var(--bg-tertiary); }
.session-item.active { background: var(--accent-color); color: white; }
.session-item.active .session-time { color: rgba(255, 255, 255, 0.8); }
.session-info { flex: 1; min-width: 0; }
.session-title { font-size: 0.9rem; font-weight: 500; margin-bottom: 0.25rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.session-time { font-size: 0.75rem; color: var(--text-secondary); }
.delete-session { background: none; border: none; color: var(--text-secondary); cursor: pointer; font-size: 1.2rem; padding: 0.25rem; border-radius: 4px; transition: all 0.2s ease; opacity: 0; }
.session-item:hover .delete-session { opacity: 1; }
.delete-session:hover { background: rgba(255, 0, 0, 0.1); color: #ff4444; }
.main-content { flex: 1; display: flex; flex-direction: column; min-width: 0; }
.header { background: var(--bg-secondary); border-bottom: 1px solid var(--border-color); padding: 1rem 2rem; }
.header-content { display: flex; justify-content: space-between; align-items: center; }
.header-left { display: flex; align-items: center; gap: 1rem; }
.sidebar-toggle { background: none; border: none; font-size: 1.2rem; cursor: pointer; color: var(--text-primary); padding: 0.5rem; border-radius: 4px; transition: all 0.2s ease; }
.sidebar-toggle:hover { background: var(--bg-tertiary); }
.title { display: flex; align-items: center; gap: 0.5rem; font-size: 1.5rem; font-weight: 600; color: var(--text-primary); }
.theme-toggle { background: var(--bg-tertiary); border: 1px solid var(--border-color); border-radius: 50%; width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; cursor: pointer; font-size: 1.2rem; transition: all 0.3s ease; }
.theme-toggle:hover { background: var(--accent-color); transform: scale(1.1); }
.chat-container { flex: 1; display: flex; flex-direction: column; background: var(--bg-primary); min-height: 0; }
.messages { flex: 1; overflow-y: auto; padding: 2rem; display: flex; flex-direction: column; gap: 1.5rem; min-height: 0; }
.message-wrapper { display: flex; width: 100%; }
.user-message { justify-content: flex-end; }
.assistant-message { justify-content: flex-start; }
.message { display: flex; align-items: flex-start; gap: 0.75rem; max-width: 80%; animation: fadeIn 0.3s ease; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
.avatar { width: 40px; height: 40px; border-radius: 50%; background: var(--bg-tertiary); display: flex; align-items: center; justify-content: center; font-size: 1.2rem; flex-shrink: 0; }
.content { background: var(--bg-secondary); padding: 1rem 1.25rem; border-radius: 16px; box-shadow: var(--shadow); position: relative; }
.user-message .content { background: var(--accent-color); color: white; border-bottom-right-radius: 4px; }
.assistant-message .content { background: var(--bg-secondary); border-bottom-left-radius: 4px; }
.message-content { line-height: 1.6; font-size: 0.95rem; }
.message-content h1, .message-content h2, .message-content h3 { margin: 0.5rem 0 0.3rem 0; color: var(--text-primary); }
.message-content h1 { font-size: 1.3rem; border-bottom: 1px solid var(--border-color); padding-bottom: 0.3rem; }
.message-content h2 { font-size: 1.1rem; }
.message-content h3 { font-size: 1rem; }
.message-content strong { font-weight: 600; color: var(--text-primary); }
.message-content em { font-style: italic; color: var(--text-secondary); }
.message-content ul { margin: 0.5rem 0; padding-left: 1.5rem; }
.message-content li { margin: 0.3rem 0; line-height: 1.5; }
.message-content p { margin: 0.5rem 0; line-height: 1.6; }
.message-content p:first-child { margin-top: 0; }
.message-content p:last-child { margin-bottom: 0; }
.message-content br { display: block; content: ""; margin: 0.3rem 0; }
.user-message .message-content { color: white; }
.user-message .message-content h1, .user-message .message-content h2, .user-message .message-content h3, .user-message .message-content strong { color: white; }
.user-message .message-content em { color: rgba(255, 255, 255, 0.9); }
.thinking-indicator { display: flex; align-items: center; gap: 0.5rem; margin-top: 0.5rem; color: var(--text-secondary); font-size: 0.85rem; }
.thinking-dots { display: flex; gap: 0.25rem; }
.thinking-dots span { width: 6px; height: 6px; background: var(--accent-color); border-radius: 50%; animation: thinking 1.4s infinite ease-in-out; }
.thinking-dots span:nth-child(1) { animation-delay: -0.32s; }
.thinking-dots span:nth-child(2) { animation-delay: -0.16s; }
@keyframes thinking { 0%, 80%, 100% { transform: scale(0.8); opacity: 0.5; } 40% { transform: scale(1.2); opacity: 1; } }
.input-area { background: var(--bg-secondary); border-top: 1px solid var(--border-color); padding: 1.5rem 2rem; }
.input-container { display: flex; gap: 1rem; align-items: flex-end; max-width: 800px; margin: 0 auto; }
.input-container textarea { flex: 1; border: 1px solid var(--border-color); border-radius: 20px; padding: 0.75rem 1rem; background: var(--bg-primary); color: var(--text-primary); font-size: 0.95rem; resize: none; outline: none; transition: all 0.3s ease; max-height: 120px; min-height: 44px; }
.input-container textarea:focus { border-color: var(--accent-color); box-shadow: 0 0 0 3px rgba(212, 175, 55, 0.1); }
.send-btn { background: var(--accent-color); color: white; border: none; border-radius: 50%; width: 44px; height: 44px; display: flex; align-items: center; justify-content: center; cursor: pointer; font-weight: 600; transition: all 0.3s ease; flex-shrink: 0; }
.send-btn:hover:not(:disabled) { background: var(--accent-hover); transform: scale(1.05); }
.send-btn:disabled { opacity: 0.5; cursor: not-allowed; }
@media (max-width: 768px) { .sidebar { position: absolute; left: 0; top: 0; height: 100vh; z-index: 30; } .sidebar-hidden { transform: translateX(-100%); } .messages { padding: 1rem; } .message { max-width: 90%; } .input-area { padding: 1rem; } .input-container { gap: 0.5rem; } .session-item:hover .delete-session { opacity: 0.7; } }
</style>
