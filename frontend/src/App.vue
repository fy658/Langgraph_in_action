<template>
  <div class="app-container">
    <!-- Header -->
    <header class="header">
      <div class="header-content">
        <div class="logo">
          <svg class="logo-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
          </svg>
          <span class="logo-text">智能客服系统</span>
        </div>
        <div class="header-status">
          <span class="status-dot" :class="{ online: isConnected }"></span>
          <span class="status-text">{{ isConnected ? 'AI客服在线' : '连接中...' }}</span>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="main-content">
      <div class="chat-container">
        <!-- Sidebar -->
        <aside class="sidebar">
          <div class="sidebar-section">
            <h3 class="sidebar-title">服务类型</h3>
            <div class="category-list">
              <div class="category-item" v-for="cat in categories" :key="cat.name">
                <span class="category-icon" :class="cat.iconClass">{{ cat.icon }}</span>
                <div class="category-info">
                  <span class="category-name">{{ cat.name }}</span>
                  <span class="category-desc">{{ cat.desc }}</span>
                </div>
              </div>
            </div>
          </div>

          <div class="sidebar-section">
            <h3 class="sidebar-title">快捷问题</h3>
            <div class="quick-questions">
              <button 
                v-for="(question, index) in quickQuestions" 
                :key="index"
                class="quick-btn"
                @click="sendQuickQuestion(question)"
              >
                {{ question }}
              </button>
            </div>
          </div>

          <div class="sidebar-section stats">
            <h3 class="sidebar-title">对话统计</h3>
            <div class="stats-grid">
              <div class="stat-item">
                <span class="stat-value">{{ messageCount }}</span>
                <span class="stat-label">消息数</span>
              </div>
              <div class="stat-item">
                <span class="stat-value">{{ responseCount }}</span>
                <span class="stat-label">回复数</span>
              </div>
            </div>
          </div>
        </aside>

        <!-- Chat Area -->
        <div class="chat-main">
          <!-- Messages -->
          <div class="messages-container" ref="messagesContainer">
            <!-- Welcome Message -->
            <div v-if="messages.length === 0" class="welcome-message">
              <div class="welcome-icon">🤖</div>
              <h2>欢迎使用智能客服系统</h2>
              <p>我是基于 LangGraph 的 AI 客服助手，可以帮您处理技术支持、账单查询等问题。</p>
              <p>请在下方输入您的问题，我会尽力为您解答！</p>
            </div>

            <!-- Chat Messages -->
            <div 
              v-for="(message, index) in messages" 
              :key="index"
              class="message fade-in"
              :class="message.type"
            >
              <div class="message-avatar">
                {{ message.type === 'user' ? '👤' : '🤖' }}
              </div>
              <div class="message-content">
                <div class="message-header">
                  <span class="message-sender">{{ message.type === 'user' ? '您' : 'AI客服' }}</span>
                  <span class="message-time">{{ message.time }}</span>
                </div>
                <div class="message-text">{{ message.text }}</div>
                
                <!-- Analysis Tags (for AI responses) -->
                <div v-if="message.analysis" class="message-analysis">
                  <span class="badge" :class="getCategoryBadgeClass(message.analysis.category)">
                    📂 {{ message.analysis.category }}
                  </span>
                  <span class="badge" :class="getSentimentBadgeClass(message.analysis.sentiment)">
                    {{ getSentimentEmoji(message.analysis.sentiment) }} {{ message.analysis.sentiment }}
                  </span>
                </div>
              </div>
            </div>

            <!-- Typing Indicator -->
            <div v-if="isLoading" class="message assistant fade-in">
              <div class="message-avatar">🤖</div>
              <div class="message-content">
                <div class="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          </div>

          <!-- Input Area -->
          <div class="input-area">
            <div class="input-wrapper">
              <textarea
                v-model="inputMessage"
                @keydown.enter.prevent="handleEnter"
                placeholder="输入您的问题..."
                rows="1"
                :disabled="isLoading"
                ref="inputField"
              ></textarea>
              <button 
                class="send-btn" 
                @click="sendMessage"
                :disabled="!inputMessage.trim() || isLoading"
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <line x1="22" y1="2" x2="11" y2="13"></line>
                  <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
                </svg>
              </button>
            </div>
            <div class="input-hint">
              按 Enter 发送消息，Shift + Enter 换行
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- Footer -->
    <footer class="footer">
      <p>Powered by LangGraph & Vue3 | 智能客服系统 v1.0</p>
    </footer>
  </div>
</template>

<script>
import { ref, onMounted, nextTick, computed } from 'vue'
import axios from 'axios'

export default {
  name: 'App',
  setup() {
    const messages = ref([])
    const inputMessage = ref('')
    const isLoading = ref(false)
    const isConnected = ref(false)
    const messagesContainer = ref(null)
    const inputField = ref(null)

    const categories = [
      { name: '技术支持', icon: '🔧', iconClass: 'technical', desc: '软件、连接等问题' },
      { name: '账单查询', icon: '💳', iconClass: 'billing', desc: '支付、发票等问题' },
      { name: '常规咨询', icon: '💬', iconClass: 'general', desc: '其他一般性问题' }
    ]

    const quickQuestions = [
      '我的网络连接不稳定，该怎么办？',
      '如何查看我的账单？',
      '你们的营业时间是什么时候？',
      '如何重置我的密码？'
    ]

    const messageCount = computed(() => messages.value.filter(m => m.type === 'user').length)
    const responseCount = computed(() => messages.value.filter(m => m.type === 'assistant').length)

    const getCurrentTime = () => {
      return new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
    }

    const scrollToBottom = async () => {
      await nextTick()
      if (messagesContainer.value) {
        messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
      }
    }

    const getCategoryBadgeClass = (category) => {
      if (!category) return 'badge-general'
      const cat = category.toLowerCase()
      if (cat.includes('technical') || cat.includes('技术')) return 'badge-technical'
      if (cat.includes('billing') || cat.includes('账单')) return 'badge-billing'
      return 'badge-general'
    }

    const getSentimentBadgeClass = (sentiment) => {
      if (!sentiment) return 'badge-neutral'
      const sent = sentiment.toLowerCase()
      if (sent.includes('positive') || sent.includes('积极')) return 'badge-positive'
      if (sent.includes('negative') || sent.includes('消极')) return 'badge-negative'
      return 'badge-neutral'
    }

    const getSentimentEmoji = (sentiment) => {
      if (!sentiment) return '😐'
      const sent = sentiment.toLowerCase()
      if (sent.includes('positive') || sent.includes('积极')) return '😊'
      if (sent.includes('negative') || sent.includes('消极')) return '😟'
      return '😐'
    }

    const sendMessage = async () => {
      const message = inputMessage.value.trim()
      if (!message || isLoading.value) return

      // Add user message
      messages.value.push({
        type: 'user',
        text: message,
        time: getCurrentTime()
      })

      inputMessage.value = ''
      isLoading.value = true
      scrollToBottom()

      try {
        const response = await axios.post('/api/chat', { query: message })
        const data = response.data

        // Add AI response
        messages.value.push({
          type: 'assistant',
          text: data.response,
          time: getCurrentTime(),
          analysis: {
            category: data.category,
            sentiment: data.sentiment
          }
        })
      } catch (error) {
        console.error('Error:', error)
        messages.value.push({
          type: 'assistant',
          text: '抱歉，处理您的请求时出现了问题。请稍后重试。',
          time: getCurrentTime()
        })
      } finally {
        isLoading.value = false
        scrollToBottom()
      }
    }

    const handleEnter = (event) => {
      if (event.shiftKey) {
        return // Allow new line
      }
      sendMessage()
    }

    const sendQuickQuestion = (question) => {
      inputMessage.value = question
      sendMessage()
    }

    const checkConnection = async () => {
      try {
        await axios.get('/health')
        isConnected.value = true
      } catch {
        // Try direct connection to backend
        try {
          await axios.get('http://localhost:8000/health')
          isConnected.value = true
        } catch {
          isConnected.value = false
        }
      }
    }

    onMounted(() => {
      checkConnection()
      inputField.value?.focus()
    })

    return {
      messages,
      inputMessage,
      isLoading,
      isConnected,
      messagesContainer,
      inputField,
      categories,
      quickQuestions,
      messageCount,
      responseCount,
      sendMessage,
      handleEnter,
      sendQuickQuestion,
      getCategoryBadgeClass,
      getSentimentBadgeClass,
      getSentimentEmoji
    }
  }
}
</script>

<style scoped>
.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

/* Header */
.header {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid var(--border-color);
  padding: 1rem 2rem;
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-content {
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.logo-icon {
  width: 32px;
  height: 32px;
  color: var(--primary-color);
}

.logo-text {
  font-size: 1.25rem;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.header-status {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.status-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: var(--neutral-color);
  animation: pulse 2s infinite;
}

.status-dot.online {
  background: var(--success-color);
}

.status-text {
  font-size: 0.875rem;
  color: var(--text-secondary);
}

/* Main Content */
.main-content {
  flex: 1;
  padding: 1.5rem;
}

.chat-container {
  max-width: 1400px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: 1.5rem;
  height: calc(100vh - 180px);
}

/* Sidebar */
.sidebar {
  background: var(--bg-secondary);
  border-radius: 1rem;
  padding: 1.5rem;
  box-shadow: var(--shadow-lg);
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  overflow-y: auto;
}

.sidebar-section {
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 1.5rem;
}

.sidebar-section:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.sidebar-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 1rem;
}

.category-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.category-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  background: var(--bg-chat);
  border-radius: 0.5rem;
  transition: transform 0.2s;
}

.category-item:hover {
  transform: translateX(4px);
}

.category-icon {
  font-size: 1.5rem;
}

.category-info {
  display: flex;
  flex-direction: column;
}

.category-name {
  font-weight: 500;
  font-size: 0.875rem;
}

.category-desc {
  font-size: 0.75rem;
  color: var(--text-secondary);
}

.quick-questions {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.quick-btn {
  text-align: left;
  padding: 0.75rem;
  background: var(--bg-chat);
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  font-size: 0.813rem;
  color: var(--text-primary);
  cursor: pointer;
  transition: all 0.2s;
}

.quick-btn:hover {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}

.stat-item {
  text-align: center;
  padding: 1rem;
  background: var(--bg-chat);
  border-radius: 0.5rem;
}

.stat-value {
  display: block;
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--primary-color);
}

.stat-label {
  font-size: 0.75rem;
  color: var(--text-secondary);
}

/* Chat Main */
.chat-main {
  background: var(--bg-secondary);
  border-radius: 1rem;
  box-shadow: var(--shadow-lg);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

/* Welcome Message */
.welcome-message {
  text-align: center;
  padding: 3rem 2rem;
  color: var(--text-secondary);
}

.welcome-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.welcome-message h2 {
  color: var(--text-primary);
  margin-bottom: 0.5rem;
}

.welcome-message p {
  max-width: 400px;
  margin: 0.5rem auto;
}

/* Messages */
.message {
  display: flex;
  gap: 0.75rem;
  max-width: 80%;
}

.message.user {
  align-self: flex-end;
  flex-direction: row-reverse;
}

.message-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--bg-chat);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  flex-shrink: 0;
}

.message.user .message-avatar {
  background: var(--primary-color);
}

.message-content {
  background: var(--bg-chat);
  padding: 1rem;
  border-radius: 1rem;
  border-top-left-radius: 0.25rem;
}

.message.user .message-content {
  background: var(--primary-color);
  color: white;
  border-top-left-radius: 1rem;
  border-top-right-radius: 0.25rem;
}

.message-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
  gap: 1rem;
}

.message-sender {
  font-weight: 600;
  font-size: 0.875rem;
}

.message-time {
  font-size: 0.75rem;
  opacity: 0.7;
}

.message-text {
  line-height: 1.6;
  white-space: pre-wrap;
}

.message-analysis {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.75rem;
  flex-wrap: wrap;
}

/* Typing Indicator */
.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 0.5rem 0;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--text-secondary);
  animation: typing 1.4s ease-in-out infinite;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

/* Input Area */
.input-area {
  padding: 1rem 1.5rem;
  border-top: 1px solid var(--border-color);
  background: var(--bg-secondary);
}

.input-wrapper {
  display: flex;
  gap: 0.75rem;
  align-items: flex-end;
}

.input-wrapper textarea {
  flex: 1;
  padding: 0.875rem 1rem;
  border: 2px solid var(--border-color);
  border-radius: 0.75rem;
  font-size: 0.938rem;
  font-family: inherit;
  resize: none;
  transition: border-color 0.2s;
  max-height: 120px;
}

.input-wrapper textarea:focus {
  outline: none;
  border-color: var(--primary-color);
}

.send-btn {
  width: 48px;
  height: 48px;
  border: none;
  border-radius: 0.75rem;
  background: var(--primary-color);
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  flex-shrink: 0;
}

.send-btn:hover:not(:disabled) {
  background: var(--primary-hover);
  transform: scale(1.05);
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.send-btn svg {
  width: 20px;
  height: 20px;
}

.input-hint {
  font-size: 0.75rem;
  color: var(--text-secondary);
  margin-top: 0.5rem;
  text-align: center;
}

/* Footer */
.footer {
  background: rgba(255, 255, 255, 0.1);
  padding: 1rem;
  text-align: center;
  color: white;
  font-size: 0.875rem;
}

/* Responsive */
@media (max-width: 900px) {
  .chat-container {
    grid-template-columns: 1fr;
  }

  .sidebar {
    display: none;
  }

  .message {
    max-width: 90%;
  }
}
</style>
