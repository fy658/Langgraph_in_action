<template>
  <div class="app-container">
    <!-- Header -->
    <header class="header">
      <div class="header-content">
        <div class="logo">
          <svg class="logo-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"></path>
          </svg>
          <span class="logo-text">AI 智能助手</span>
        </div>
        
        <!-- Mode Toggle -->
        <div class="mode-toggle">
          <button 
            class="mode-btn"
            :class="{ active: currentMode === 'support' }"
            @click="currentMode = 'support'"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
            </svg>
            客服支持
          </button>
          <button 
            class="mode-btn"
            :class="{ active: currentMode === 'travel' }"
            @click="currentMode = 'travel'"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M3 18v-6a9 9 0 0 1 18 0v6"></path>
              <path d="M21 19a2 2 0 0 1-2 2h-1a2 2 0 0 1-2-2v-3a2 2 0 0 1 2-2h3zM3 19a2 2 0 0 0 2 2h1a2 2 0 0 0 2-2v-3a2 2 0 0 0-2-2H3z"></path>
            </svg>
            旅游规划
          </button>
        </div>

        <div class="header-status">
          <span class="status-dot" :class="{ online: isConnected }"></span>
          <span class="status-text">{{ isConnected ? 'AI 在线' : '连接中...' }}</span>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="main-content">
      <div class="content-wrapper">
        <!-- Customer Support Module -->
        <CustomerSupport v-if="currentMode === 'support'" />
        
        <!-- Travel Planner Module -->
        <TravelPlanner v-else-if="currentMode === 'travel'" />
      </div>
    </main>

    <!-- Footer -->
    <footer class="footer">
      <p>Powered by LangGraph & Vue3 | AI 智能助手系统 v2.0</p>
    </footer>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import CustomerSupport from './components/CustomerSupport.vue'
import TravelPlanner from './components/TravelPlanner.vue'

export default {
  name: 'App',
  components: {
    CustomerSupport,
    TravelPlanner
  },
  setup() {
    const currentMode = ref('support') // 'support' or 'travel'
    const isConnected = ref(false)

    const checkConnection = async () => {
      try {
        await axios.get('/health')
        isConnected.value = true
      } catch {
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
    })

    return {
      currentMode,
      isConnected
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
  gap: 2rem;
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

/* Mode Toggle */
.mode-toggle {
  display: flex;
  gap: 0.5rem;
  background: var(--bg-chat);
  padding: 0.25rem;
  border-radius: 0.75rem;
}

.mode-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 1.25rem;
  background: transparent;
  border: none;
  border-radius: 0.5rem;
  color: var(--text-secondary);
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.mode-btn svg {
  width: 18px;
  height: 18px;
}

.mode-btn:hover {
  color: var(--text-primary);
}

.mode-btn.active {
  background: white;
  color: var(--primary-color);
  box-shadow: var(--shadow-sm);
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
  display: flex;
}

.content-wrapper {
  width: 100%;
  max-width: 1400px;
  margin: 0 auto;
  background: var(--bg-secondary);
  border-radius: 1rem;
  box-shadow: var(--shadow-lg);
  overflow: hidden;
  display: flex;
  flex-direction: column;
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
  .header-content {
    flex-direction: column;
    gap: 1rem;
  }

  .mode-toggle {
    width: 100%;
  }

  .mode-btn {
    flex: 1;
    justify-content: center;
  }
}
</style>
