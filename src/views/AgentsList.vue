<template>
  <div class="agents-list">
    <h1>智能体列表</h1>
    
    <div v-if="loading" class="loading-container">
      <div class="loading-indicator">
        <span></span><span></span><span></span>
      </div>
      <p>正在加载智能体列表...</p>
    </div>
    
    <div v-else-if="error" class="error-container">
      <p class="error-message">{{ error }}</p>
      <button @click="loadAgents" class="retry-btn">重试</button>
    </div>
    
    <div v-else-if="agents.length === 0" class="empty-container">
      <p>暂无智能体</p>
      <router-link to="/agent/create" class="create-btn">
        创建智能体
      </router-link>
    </div>
    
    <div v-else class="agents-grid">
      <div v-for="agent in agents" :key="agent.id" class="agent-card">
        <div class="agent-header">
          <div class="agent-avatar">
            <img 
              :src="agent.avatar || getDefaultAvatar(agent.name)" 
              alt="智能体头像" 
              @error="handleImageError"
            >
          </div>
          <h3>{{ agent.name }}</h3>
        </div>
        
        <p class="agent-description">{{ agent.description }}</p>
        <div class="agent-info">
          <span class="agent-date">创建于: {{ formatDate(agent.createdAt) }}</span>
        </div>
        
        <div class="agent-actions">
          <router-link :to="'/agent/' + agent.id" class="action-btn">
            查看详情
          </router-link>
          <button @click="startDialog(agent.id)" class="action-btn dialog-btn">
            开始对话
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useAgentStore } from '../store/agents';
import { storeToRefs } from 'pinia';
import { useRouter } from 'vue-router';

const router = useRouter();
const agentStore = useAgentStore();
const { agents } = storeToRefs(agentStore);

const loading = ref(false);
const error = ref(null);

// 加载智能体列表
async function loadAgents() {
  try {
    loading.value = true;
    error.value = null;
    
    console.log("开始加载智能体列表...");
    const result = await agentStore.loadAgents();
    console.log("智能体加载结果:", result);
    
    if (!result.success) {
      error.value = result.message || '加载智能体失败';
      console.error("智能体加载失败:", error.value);
    } else {
      console.log("成功加载智能体，数量:", agents.value.length);
    }
  } catch (err) {
    console.error('加载智能体列表出错:', err);
    error.value = err.message || '加载智能体时发生错误';
  } finally {
    loading.value = false;
  }
}

// 开始与智能体对话
async function startDialog(agentId) {
  try {
    loading.value = true;
    
    // 创建对话
    const result = await agentStore.createConversation(
      parseInt(agentId),
      0 // 用户ID为0
    );
    
    if (result && result.success) {
      // 导航到对话页面
      router.push(`/dialog/${agentId}`);
    } else {
      alert('创建对话失败: ' + (result ? result.message : '未知错误'));
    }
  } catch (error) {
    console.error('创建对话出错:', error);
    alert('创建对话时出错: ' + (error.message || '未知错误'));
  } finally {
    loading.value = false;
  }
}

// 格式化日期
function formatDate(dateString) {
  try {
    if (!dateString) return '未知日期';
    const date = new Date(dateString);
    return date.toLocaleDateString('zh-CN');
  } catch (e) {
    return dateString || '未知日期';
  }
}

// 图片加载失败处理
function handleImageError(e) {
  const name = e.target.closest('.agent-card').querySelector('h3').textContent || 'AI';
  e.target.src = getDefaultAvatar(name);
}

// 生成默认头像
function getDefaultAvatar(name) {
  const initials = name.substring(0, 2).toUpperCase();
  const isDarkMode = document.body.classList.contains('light-mode') ? false : true;
  
  // 浅色/暗色模式不同颜色
  const darkModeColors = ['#00ff00', '#ff5722', '#2196f3', '#9c27b0', '#ffeb3b'];
  const lightModeColors = ['#006633', '#b34700', '#0d47a1', '#4a148c', '#ff8f00'];
  
  const colors = isDarkMode ? darkModeColors : lightModeColors;
  const bgColor = isDarkMode ? '%23000' : '%23f5f5f5';
  
  const colorIndex = Math.abs(name.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0)) % colors.length;
  const color = colors[colorIndex];
  
  return `data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 100 100"><rect width="100" height="100" fill="${bgColor}"/><text x="50" y="50" font-family="Arial" font-size="35" fill="${color}" text-anchor="middle" dominant-baseline="middle">${initials}</text></svg>`;
}

// 组件加载时获取智能体列表
onMounted(() => {
  loadAgents();
});
</script>

<style scoped>
.agents-list {
  padding: 2rem;
  color: var(--text-color);
}

h1 {
  text-align: center;
  margin-bottom: 2rem;
  color: var(--primary-color);
  text-shadow: var(--text-shadow);
}

.agents-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

.agent-card {
  background: rgba(0, 255, 0, 0.1);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 1.5rem;
  transition: all 0.3s ease;
}

.light-mode .agent-card {
  background: rgba(0, 102, 51, 0.05);
}

.agent-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 0 20px rgba(0, 255, 0, 0.2);
}

.light-mode .agent-card:hover {
  box-shadow: 0 0 20px rgba(0, 102, 51, 0.2);
}

.agent-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.agent-avatar {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  overflow: hidden;
  border: 2px solid var(--primary-color);
  background: var(--bg-color);
}

.agent-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.agent-description {
  color: var(--text-color);
  margin-bottom: 1rem;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.agent-info {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 1rem;
}

.agent-date {
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.agent-actions {
  display: flex;
  justify-content: space-between;
}

.action-btn {
  padding: 0.5rem 1rem;
  background: rgba(0, 255, 0, 0.2);
  border: 1px solid var(--primary-color);
  color: var(--primary-color);
  text-decoration: none;
  border-radius: 4px;
  transition: all 0.3s ease;
}

.light-mode .action-btn {
  background: rgba(0, 102, 51, 0.1);
}

.dialog-btn {
  background: rgba(0, 255, 0, 0.1);
}

.light-mode .dialog-btn {
  background: rgba(0, 102, 51, 0.05);
}

.action-btn:hover {
  background: rgba(0, 255, 0, 0.3);
  box-shadow: 0 0 10px rgba(0, 255, 0, 0.3);
}

.light-mode .action-btn:hover {
  background: rgba(0, 102, 51, 0.2);
  box-shadow: 0 0 10px rgba(0, 102, 51, 0.3);
}

/* 加载状态 */
.loading-container, .error-container, .empty-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 1rem;
  text-align: center;
}

.loading-indicator {
  display: flex;
  gap: 4px;
  margin-bottom: 1rem;
}

.loading-indicator span {
  display: inline-block;
  width: 12px;
  height: 12px;
  background-color: var(--primary-color);
  border-radius: 50%;
  animation: bounce 1.4s infinite ease-in-out both;
}

.loading-indicator span:nth-child(1) {
  animation-delay: -0.32s;
}

.loading-indicator span:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}

.error-message {
  color: #ff3333;
  margin-bottom: 1rem;
}

.retry-btn, .create-btn {
  padding: 0.5rem 1.5rem;
  background: rgba(0, 255, 0, 0.2);
  border: 1px solid var(--primary-color);
  color: var(--primary-color);
  text-decoration: none;
  border-radius: 4px;
  transition: all 0.3s ease;
  cursor: pointer;
}

.retry-btn:hover, .create-btn:hover {
  background: rgba(0, 255, 0, 0.3);
  box-shadow: 0 0 10px rgba(0, 255, 0, 0.3);
}
</style> 