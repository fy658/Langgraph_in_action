<template>
  <div class="travel-planner">
    <!-- Form Section -->
    <div class="planner-form" v-if="!generatedPlan">
      <div class="form-header">
        <div class="form-icon">✈️</div>
        <h2>智能旅游规划助手</h2>
        <p>告诉我您的目的地和兴趣，我将为您定制专属行程</p>
      </div>

      <div class="form-content">
        <!-- City Input -->
        <div class="form-group">
          <label class="form-label">
            <span class="label-icon">📍</span>
            目的地城市
          </label>
          <input
            v-model="city"
            type="text"
            class="form-input"
            placeholder="例如：北京、东京、巴黎..."
            @keydown.enter="generatePlan"
          />
        </div>

        <!-- Interests Selection -->
        <div class="form-group">
          <label class="form-label">
            <span class="label-icon">❤️</span>
            旅行兴趣 (至少选择一个)
          </label>
          <div class="interests-grid">
            <button
              v-for="interest in availableInterests"
              :key="interest.value"
              class="interest-btn"
              :class="{ active: selectedInterests.includes(interest.value) }"
              @click="toggleInterest(interest.value)"
            >
              <span class="interest-icon">{{ interest.icon }}</span>
              <span class="interest-name">{{ interest.name }}</span>
            </button>
          </div>
        </div>

        <!-- Custom Interest Input -->
        <div class="form-group">
          <label class="form-label">
            <span class="label-icon">➕</span>
            其他兴趣 (可选)
          </label>
          <div class="custom-interest-input">
            <input
              v-model="customInterest"
              type="text"
              class="form-input"
              placeholder="输入其他兴趣并按回车添加"
              @keydown.enter.prevent="addCustomInterest"
            />
            <button class="add-btn" @click="addCustomInterest">添加</button>
          </div>
          <div v-if="customInterests.length > 0" class="custom-interests-tags">
            <span
              v-for="(interest, index) in customInterests"
              :key="index"
              class="interest-tag"
            >
              {{ interest }}
              <button class="remove-tag" @click="removeCustomInterest(index)">×</button>
            </span>
          </div>
        </div>

        <!-- Generate Button -->
        <button
          class="generate-btn"
          :disabled="!canGenerate || isGenerating"
          @click="generatePlan"
        >
          <span v-if="!isGenerating">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M5 12h14M12 5l7 7-7 7"/>
            </svg>
            生成专属行程
          </span>
          <span v-else class="loading">
            <span class="spinner"></span>
            正在生成行程...
          </span>
        </button>
      </div>
    </div>

    <!-- Itinerary Display -->
    <div class="itinerary-display fade-in" v-else>
      <div class="itinerary-header">
        <div class="header-top">
          <div class="destination">
            <span class="destination-icon">🏙️</span>
            <h2>{{ planData.city }} 一日游行程</h2>
          </div>
          <button class="new-plan-btn" @click="resetPlan">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="1 4 1 10 7 10"></polyline>
              <path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10"></path>
            </svg>
            重新规划
          </button>
        </div>
        <div class="selected-interests">
          <span class="interests-label">您的兴趣：</span>
          <span
            v-for="(interest, index) in planData.interests"
            :key="index"
            class="interest-badge"
          >
            {{ interest }}
          </span>
        </div>
      </div>

      <div class="itinerary-content">
        <div class="itinerary-text" v-html="formattedItinerary"></div>
      </div>

      <div class="itinerary-actions">
        <button class="action-btn secondary" @click="copyItinerary">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
            <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
          </svg>
          复制行程
        </button>
        <button class="action-btn primary" @click="shareItinerary">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="18" cy="5" r="3"></circle>
            <circle cx="6" cy="12" r="3"></circle>
            <circle cx="18" cy="19" r="3"></circle>
            <line x1="8.59" y1="13.51" x2="15.42" y2="17.49"></line>
            <line x1="15.41" y1="6.51" x2="8.59" y2="10.49"></line>
          </svg>
          分享行程
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

export default {
  name: 'TravelPlanner',
  setup() {
    const city = ref('')
    const selectedInterests = ref([])
    const customInterest = ref('')
    const customInterests = ref([])
    const availableInterests = ref([])
    const isGenerating = ref(false)
    const generatedPlan = ref(false)
    const planData = ref(null)

    const canGenerate = computed(() => {
      return city.value.trim() !== '' && 
             (selectedInterests.value.length > 0 || customInterests.value.length > 0)
    })

    const allInterests = computed(() => {
      return [...selectedInterests.value, ...customInterests.value]
    })

    const formattedItinerary = computed(() => {
      if (!planData.value) return ''
      
      // Convert markdown-style formatting to HTML
      let html = planData.value.itinerary
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/^- (.+)$/gm, '<li>$1</li>')
        .replace(/^• (.+)$/gm, '<li>$1</li>')
        .replace(/\n\n/g, '</p><p>')
        .replace(/\n/g, '<br>')
      
      // Wrap list items in ul tags
      html = html.replace(/(<li>.*?<\/li>)/gs, '<ul>$1</ul>')
      html = html.replace(/<\/ul><br><ul>/g, '')
      
      return `<p>${html}</p>`
    })

    const toggleInterest = (interest) => {
      const index = selectedInterests.value.indexOf(interest)
      if (index > -1) {
        selectedInterests.value.splice(index, 1)
      } else {
        selectedInterests.value.push(interest)
      }
    }

    const addCustomInterest = () => {
      const interest = customInterest.value.trim()
      if (interest && !customInterests.value.includes(interest)) {
        customInterests.value.push(interest)
        customInterest.value = ''
      }
    }

    const removeCustomInterest = (index) => {
      customInterests.value.splice(index, 1)
    }

    const generatePlan = async () => {
      if (!canGenerate.value || isGenerating.value) return

      isGenerating.value = true

      try {
        const response = await axios.post('/api/travel/plan', {
          city: city.value,
          interests: allInterests.value
        })

        planData.value = response.data
        generatedPlan.value = true
      } catch (error) {
        console.error('Error generating plan:', error)
        alert('生成行程时出错，请稍后重试')
      } finally {
        isGenerating.value = false
      }
    }

    const resetPlan = () => {
      generatedPlan.value = false
      planData.value = null
    }

    const copyItinerary = async () => {
      try {
        const text = planData.value.itinerary
        await navigator.clipboard.writeText(text)
        alert('行程已复制到剪贴板！')
      } catch (error) {
        console.error('Copy failed:', error)
      }
    }

    const shareItinerary = () => {
      if (navigator.share) {
        navigator.share({
          title: `${planData.value.city} 旅行行程`,
          text: planData.value.itinerary
        })
      } else {
        copyItinerary()
      }
    }

    const loadInterests = async () => {
      try {
        const response = await axios.get('/api/travel/interests')
        availableInterests.value = response.data.interests
      } catch (error) {
        console.error('Error loading interests:', error)
        // Fallback interests
        availableInterests.value = [
          { name: '美食', value: 'food', icon: '🍜' },
          { name: '历史', value: 'history', icon: '🏛️' },
          { name: '艺术', value: 'art', icon: '🎨' },
          { name: '自然', value: 'nature', icon: '🏞️' },
          { name: '购物', value: 'shopping', icon: '🛍️' },
          { name: '夜生活', value: 'nightlife', icon: '🌃' },
        ]
      }
    }

    onMounted(() => {
      loadInterests()
    })

    return {
      city,
      selectedInterests,
      customInterest,
      customInterests,
      availableInterests,
      isGenerating,
      generatedPlan,
      planData,
      canGenerate,
      formattedItinerary,
      toggleInterest,
      addCustomInterest,
      removeCustomInterest,
      generatePlan,
      resetPlan,
      copyItinerary,
      shareItinerary
    }
  }
}
</script>

<style scoped>
.travel-planner {
  width: 100%;
  height: 100%;
  overflow-y: auto;
}

/* Form Section */
.planner-form {
  max-width: 700px;
  margin: 0 auto;
  padding: 2rem;
}

.form-header {
  text-align: center;
  margin-bottom: 2.5rem;
}

.form-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.form-header h2 {
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 0.5rem;
}

.form-header p {
  color: var(--text-secondary);
  font-size: 1rem;
}

.form-content {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.form-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 600;
  color: var(--text-primary);
  font-size: 0.938rem;
}

.label-icon {
  font-size: 1.25rem;
}

.form-input {
  padding: 0.875rem 1rem;
  border: 2px solid var(--border-color);
  border-radius: 0.75rem;
  font-size: 1rem;
  font-family: inherit;
  transition: border-color 0.2s;
}

.form-input:focus {
  outline: none;
  border-color: var(--primary-color);
}

/* Interests Grid */
.interests-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 0.75rem;
}

.interest-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem 0.75rem;
  background: var(--bg-chat);
  border: 2px solid var(--border-color);
  border-radius: 0.75rem;
  cursor: pointer;
  transition: all 0.2s;
}

.interest-btn:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.interest-btn.active {
  background: var(--primary-color);
  border-color: var(--primary-color);
  color: white;
}

.interest-icon {
  font-size: 2rem;
}

.interest-name {
  font-size: 0.875rem;
  font-weight: 500;
}

/* Custom Interest Input */
.custom-interest-input {
  display: flex;
  gap: 0.5rem;
}

.custom-interest-input .form-input {
  flex: 1;
}

.add-btn {
  padding: 0.875rem 1.5rem;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 0.75rem;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
}

.add-btn:hover {
  background: var(--primary-hover);
}

.custom-interests-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.interest-tag {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  background: var(--bg-chat);
  border: 1px solid var(--border-color);
  border-radius: 9999px;
  font-size: 0.875rem;
}

.remove-tag {
  background: none;
  border: none;
  color: var(--text-secondary);
  font-size: 1.25rem;
  cursor: pointer;
  padding: 0;
  line-height: 1;
}

.remove-tag:hover {
  color: var(--danger-color);
}

/* Generate Button */
.generate-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 1rem 2rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 0.75rem;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  margin-top: 1rem;
}

.generate-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 16px rgba(102, 126, 234, 0.4);
}

.generate-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.generate-btn svg {
  width: 20px;
  height: 20px;
}

.loading {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.spinner {
  width: 20px;
  height: 20px;
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Itinerary Display */
.itinerary-display {
  max-width: 900px;
  margin: 0 auto;
  padding: 2rem;
}

.itinerary-header {
  margin-bottom: 2rem;
}

.header-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.destination {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.destination-icon {
  font-size: 2.5rem;
}

.destination h2 {
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--text-primary);
}

.new-plan-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.25rem;
  background: var(--bg-chat);
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  color: var(--text-primary);
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.new-plan-btn:hover {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

.new-plan-btn svg {
  width: 18px;
  height: 18px;
}

.selected-interests {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.5rem;
}

.interests-label {
  color: var(--text-secondary);
  font-size: 0.875rem;
}

.interest-badge {
  padding: 0.375rem 0.875rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 9999px;
  font-size: 0.813rem;
  font-weight: 500;
}

.itinerary-content {
  background: var(--bg-chat);
  padding: 2rem;
  border-radius: 1rem;
  margin-bottom: 1.5rem;
  line-height: 1.8;
}

.itinerary-text {
  color: var(--text-primary);
}

.itinerary-text :deep(strong) {
  color: var(--primary-color);
  font-weight: 600;
}

.itinerary-text :deep(ul) {
  margin: 1rem 0;
  padding-left: 1.5rem;
}

.itinerary-text :deep(li) {
  margin: 0.5rem 0;
}

.itinerary-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.875rem 1.5rem;
  border: none;
  border-radius: 0.75rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.action-btn svg {
  width: 18px;
  height: 18px;
}

.action-btn.primary {
  background: var(--primary-color);
  color: white;
}

.action-btn.primary:hover {
  background: var(--primary-hover);
  transform: translateY(-2px);
}

.action-btn.secondary {
  background: var(--bg-secondary);
  color: var(--text-primary);
  border: 2px solid var(--border-color);
}

.action-btn.secondary:hover {
  background: var(--bg-chat);
}

@media (max-width: 640px) {
  .interests-grid {
    grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  }

  .header-top {
    flex-direction: column;
    gap: 1rem;
  }

  .itinerary-actions {
    flex-direction: column;
  }
}
</style>
