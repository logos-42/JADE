<template>
  <div class="agent-dialog">
    <div class="header">
      <div class="header-info">
        <h1>智能体对话</h1>
        <div class="participants" v-if="agent">
          <div class="participant">
            <div class="participant-avatar">
              <img src="/default-avatar.png" alt="智能体头像">
            </div>
            <div class="participant-name">{{ agent.name }}</div>
          </div>
          
          <div class="participant-divider" v-if="partnerAgent">
            <span>与</span>
          </div>
          
          <div class="participant" v-if="partnerAgent">
            <div class="participant-avatar">
              <img src="/default-avatar.png" alt="智能体头像">
            </div>
            <div class="participant-name">{{ partnerAgent.name }}</div>
          </div>
        </div>
      </div>
      <div class="header-actions">
        <div class="agent-selector" v-if="!partnerAgent">
          <select v-model="selectedAgentId" @change="onAgentChange">
            <option value="">选择对话对象</option>
            <option v-for="a in otherAgents" :key="a.id" :value="a.id">
              {{ a.name }}
            </option>
          </select>
        </div>
        <router-link :to="'/agent/' + agentId" class="back-btn">返回详情</router-link>
      </div>
    </div>
    
    <div class="chat-container" v-if="agent">
      <div class="messages" ref="messagesContainer">
        <div v-for="(message, index) in displayMessages" :key="index" 
             :class="['message', getMessageClass(message)]">
          <div class="message-sender" v-if="message.type !== 'system' && message.type !== 'error' && message.type !== 'pending'">
            {{ getSenderName(message.senderId) }}
          </div>
          <div v-if="message.type === 'pending'" class="loading-indicator">
            <span></span><span></span><span></span>
          </div>
          <div v-else-if="message.type === 'system'" class="system-message-content">
            {{ message.content }}
          </div>
          <div v-else-if="message.type === 'error'" class="error-message-content">
            {{ message.error || '发送失败' }}
          </div>
          <div v-else class="message-content" v-html="formatMessageContent(message.content)"></div>
          <div class="message-time" v-if="message.type !== 'pending'">{{ formatTime(message.timestamp) }}</div>
        </div>
      </div>
      
      <div class="input-area">
        <textarea 
          v-model="userInput" 
          @keydown.enter.prevent="sendMessage"
          placeholder="输入消息..." 
          rows="3"
          :disabled="isInputDisabled"
        ></textarea>
        <button @click="sendMessage" class="send-btn" :disabled="isInputDisabled">
          {{ isInputDisabled ? '等待中...' : '发送' }}
        </button>
      </div>
    </div>
    
    <div class="error" v-else-if="!loading">
      <p>找不到该智能体信息</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick, watch, onUnmounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useAgentStore } from '../store/agents';
import { storeToRefs } from 'pinia';
import { marked } from 'marked';

const route = useRoute();
const router = useRouter();
const agentStore = useAgentStore();
const { conversations } = storeToRefs(agentStore);

const agentId = parseInt(route.params.id);
const partnerAgentId = ref(parseInt(route.query.partner) || null);
const loading = ref(true);
const userInput = ref('');
const messagesContainer = ref(null);
const selectedAgentId = ref('');
const wsConnection = ref(null);

// 获取智能体信息
const agent = computed(() => {
  return agentStore.getAgentById(agentId);
});

// 获取对话伙伴智能体
const partnerAgent = computed(() => {
  if (!partnerAgentId.value) return null;
  return agentStore.getAgentById(partnerAgentId.value);
});

// 获取其他可选择的智能体
const otherAgents = computed(() => {
  if (!agent.value) return [];
  return agentStore.agents.filter(a => a.id !== agent.value.id);
});

// 获取当前对话
const currentConversation = computed(() => {
  return agentStore.getCurrentConversation;
});

// 获取对话消息
const displayMessages = computed(() => {
  if (!currentConversation.value) return [];
  return currentConversation.value.messages || [];
});

// 是否禁用输入
const isInputDisabled = computed(() => {
  if (!currentConversation.value) return true;
  const hasPendingMessage = displayMessages.value.some(m => m.type === 'pending');
  return hasPendingMessage;
});

// 根据消息类型获取样式类
function getMessageClass(message) {
  if (message.type === 'system') return 'system-message';
  if (message.type === 'error') return 'error-message';
  if (message.type === 'pending') return 'loading-message';
  
  // 根据发送者ID确定类名
  if (message.senderId === '0') return 'user-message';
  if (message.senderId === agentId.toString()) return 'agent-message';
  if (partnerAgentId.value && message.senderId === partnerAgentId.value.toString()) return 'partner-message';
  
  return 'other-message';
}

// 选择对话智能体
function onAgentChange() {
  if (selectedAgentId.value) {
    const partnerId = parseInt(selectedAgentId.value);
    // 更新URL，但不刷新页面
    router.replace({
      path: route.path,
      query: { partner: partnerId }
    });
    
    partnerAgentId.value = partnerId;
    
    // 关闭现有WebSocket连接
    closeWebSocket();
    
    // 创建新对话
    createConversation();
  }
}

// 根据ID获取发送者名称
function getSenderName(sender) {
  if (sender === '0') return '你';
  if (sender === 'SYSTEM') return '系统';
  if (sender === agentId.toString()) return agent.value.name;
  if (partnerAgent.value && sender === partnerAgent.value.id.toString()) return partnerAgent.value.name;
  return `智能体${sender}`;
}

// 格式化时间
function formatTime(timestamp) {
  if (!timestamp) return '';
  const date = new Date(timestamp);
  return date.toLocaleString();
}

// 格式化消息内容（支持markdown）
function formatMessageContent(content) {
  try {
    if (!content) return '';
    
    // 将Markdown转换为HTML
    try {
      return marked(content);
    } catch (e) {
      // 如果marked转换失败，使用简单的HTML转义
      return content
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/\n/g, '<br>');
    }
  } catch (error) {
    console.error('格式化消息内容出错:', error);
    return String(content || '');
  }
}

// 创建对话
async function createConversation() {
  try {
    loading.value = true;
    
    if (!agent.value) {
      console.error('智能体不存在');
      loading.value = false;
      return false;
    }
    
    // 确定对话参与者
    const participant1 = agentId;
    const participant2 = partnerAgentId.value || 0; // 0表示用户
    
    // 创建对话
    const result = await agentStore.createConversation(participant1, participant2);
    
    if (result && result.success) {
      console.log('对话创建成功:', result.conversationId);
      
      // 建立WebSocket连接
      setupWebSocket();
      
      loading.value = false;
      return true;
    } else {
      console.error('对话创建失败:', result ? result.message : '未知错误');
      loading.value = false;
      return false;
    }
  } catch (error) {
    console.error('创建对话时出错:', error);
    loading.value = false;
    return false;
  }
}

// 发送消息
async function sendMessage() {
  if (!userInput.value.trim() || isInputDisabled.value) return;
  
  // 缓存输入内容
  const messageContent = userInput.value;
  userInput.value = '';
  
  // 如果没有对话，先创建对话
  if (!currentConversation.value) {
    const created = await createConversation();
    if (!created) return;
  }
  
  // 发送消息
  try {
    const result = await agentStore.sendMessage(
      currentConversation.value.id,
      '0', // 用户ID固定为0
      messageContent
    );
    
    if (!result.success) {
      console.error('发送消息失败:', result.message);
    }
  } catch (error) {
    console.error('发送消息时出错:', error);
  }
}

// 设置WebSocket连接
function setupWebSocket() {
  // 关闭现有连接
  closeWebSocket();
  
  // 创建新连接
  wsConnection.value = agentStore.connectWebSocket('0'); // 用户ID固定为0
}

// 关闭WebSocket连接
function closeWebSocket() {
  if (wsConnection.value) {
    try {
      wsConnection.value.close();
    } catch (e) {
      console.error('关闭WebSocket连接时出错:', e);
    }
    wsConnection.value = null;
  }
}

// 滚动到最新消息
function scrollToBottom() {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
    }
  });
}

// 监听消息变化，自动滚动
watch(displayMessages, () => {
  scrollToBottom();
});

// 组件挂载时加载智能体和创建对话
onMounted(async () => {
  // 如果store中没有智能体，加载智能体列表
  if (agentStore.agents.length === 0) {
    await agentStore.loadAgents();
  }
  
  // 初始检查智能体是否存在
  if (agent.value) {
    // 创建对话
    await createConversation();
  }
  
  loading.value = false;
});

// 组件卸载时关闭WebSocket
onUnmounted(() => {
  closeWebSocket();
});
</script>

<style scoped>
.agent-dialog {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: #f5f5f5;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  background-color: #333;
  color: white;
  box-shadow: 0 2px 5px rgba(0,0,0,0.2);
}

.header-info {
  display: flex;
  flex-direction: column;
}

.header h1 {
  margin: 0;
  font-size: 1.5rem;
}

.participants {
  display: flex;
  align-items: center;
  margin-top: 10px;
}

.participant {
  display: flex;
  align-items: center;
}

.participant-avatar {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  overflow: hidden;
  margin-right: 8px;
}

.participant-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.participant-divider {
  margin: 0 10px;
  color: #999;
}

.header-actions {
  display: flex;
  gap: 15px;
}

.agent-selector select {
  padding: 8px 12px;
  border-radius: 4px;
  border: 1px solid #ddd;
  background-color: white;
}

.back-btn {
  display: inline-block;
  padding: 8px 12px;
  background-color: #4CAF50;
  color: white;
  text-decoration: none;
  border-radius: 4px;
  border: none;
  cursor: pointer;
  font-size: 14px;
}

.chat-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 20px;
  overflow: hidden;
}

.messages {
  flex: 1;
  overflow-y: auto;
  margin-bottom: 20px;
  padding: 10px;
}

.message {
  margin-bottom: 15px;
  max-width: 80%;
  padding: 10px;
  border-radius: 10px;
  position: relative;
}

.user-message {
  background-color: #e1f5fe;
  margin-left: auto;
  border-top-right-radius: 0;
}

.agent-message {
  background-color: #f5f5f5;
  margin-right: auto;
  border-top-left-radius: 0;
}

.partner-message {
  background-color: #e8f5e9;
  margin-right: auto;
  border-top-left-radius: 0;
}

.system-message {
  background-color: #f9f9f9;
  margin: 10px auto;
  max-width: 90%;
  text-align: center;
  color: #666;
  font-style: italic;
}

.error-message {
  background-color: #ffebee;
  margin: 10px auto;
  max-width: 90%;
  text-align: center;
  color: #d32f2f;
}

.loading-message {
  background-color: #f5f5f5;
  margin-right: auto;
  border-top-left-radius: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 40px;
}

.message-sender {
  font-weight: bold;
  margin-bottom: 5px;
}

.message-content {
  word-break: break-word;
}

.system-message-content {
  color: #666;
}

.error-message-content {
  color: #d32f2f;
}

.message-time {
  font-size: 0.75rem;
  color: #999;
  text-align: right;
  margin-top: 5px;
}

.loading-indicator {
  display: flex;
  gap: 4px;
}

.loading-indicator span {
  display: inline-block;
  width: 8px;
  height: 8px;
  background-color: #999;
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

.input-area {
  display: flex;
  gap: 10px;
  background-color: white;
  padding: 15px;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

textarea {
  flex: 1;
  border: 1px solid #ddd;
  border-radius: 5px;
  padding: 10px;
  resize: none;
  font-family: inherit;
  font-size: 1rem;
}

.send-btn {
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 5px;
  padding: 0 20px;
  cursor: pointer;
  font-weight: bold;
}

.send-btn:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.error {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  padding: 20px;
  color: #d32f2f;
  font-size: 1.2rem;
}

/* 让代码块等markdown内容更美观 */
:deep(pre) {
  background-color: #f1f1f1;
  padding: 10px;
  border-radius: 5px;
  overflow-x: auto;
}

:deep(code) {
  background-color: #f1f1f1;
  padding: 2px 4px;
  border-radius: 3px;
  font-family: monospace;
}

:deep(blockquote) {
  border-left: 3px solid #ddd;
  margin-left: 0;
  padding-left: 10px;
  color: #666;
}

:deep(a) {
  color: #2196F3;
  text-decoration: none;
}

:deep(a:hover) {
  text-decoration: underline;
}
</style> 