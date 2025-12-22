<template>
  <div class="customer-support">
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
</template>

<script>
import { ref, onMounted, nextTick } from 'vue'
import axios from 'axios'

export default {
  name: 'CustomerSupport',
  setup() {
    const messages = ref([])
    const inputMessage = ref('')
    const isLoading = ref(false)
    const messagesContainer = ref(null)
    const inputField = ref(null)

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

    onMounted(() => {
      inputField.value?.focus()
    })

    return {
      messages,
      inputMessage,
      isLoading,
      messagesContainer,
      inputField,
      sendMessage,
      handleEnter,
      getCategoryBadgeClass,
      getSentimentBadgeClass,
      getSentimentEmoji
    }
  }
}
</script>

<style scoped>
.customer-support {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--bg-secondary);
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

@media (max-width: 900px) {
  .message {
    max-width: 90%;
  }
}
</style>
