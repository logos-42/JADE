<template>
  <div class="cyber-terminal">
    <div class="cyber-terminal__header">
      <div class="cyber-terminal__title">{{ title }}</div>
      <div class="cyber-terminal__status">
        <div class="cyber-terminal__status-dot"></div>
        <span>{{ status }}</span>
      </div>
      <div class="cyber-terminal__controls">
        <button 
          class="cyber-terminal__control cyber-terminal__control--minimize"
          @click="$emit('minimize')"
        ></button>
        <button 
          class="cyber-terminal__control cyber-terminal__control--maximize"
          @click="$emit('maximize')"
        ></button>
        <button 
          class="cyber-terminal__control cyber-terminal__control--close"
          @click="$emit('close')"
        ></button>
      </div>
    </div>
    <div class="cyber-terminal__screen" ref="screen">
      <div 
        v-for="(message, index) in messages" 
        :key="index"
        :class="['cyber-terminal__message', `cyber-terminal__message--${message.type}`]"
      >
        <div class="cyber-terminal__message-header">
          <span class="cyber-terminal__message-timestamp">{{ formatTime(message.timestamp) }}</span>
          <span class="cyber-terminal__message-user">{{ message.sender }}</span>
        </div>
        <div 
          class="cyber-terminal__message-content"
          v-if="message.content"
          v-html="formatContent(message.content)"
        ></div>
        <div 
          v-if="message.type === 'loading'"
          class="cyber-terminal__loading"
        >
          <span class="dot"></span>
          <span class="dot"></span>
          <span class="dot"></span>
        </div>
      </div>
      <div class="cyber-terminal__scan-line"></div>
    </div>
    <div class="cyber-terminal__input-area" v-if="showInput">
      <div class="cyber-terminal__prompt">></div>
      <input
        ref="input"
        type="text"
        class="cyber-terminal__input"
        :placeholder="inputPlaceholder"
        v-model="inputValue"
        @keyup.enter="sendMessage"
        :disabled="inputDisabled"
      />
    </div>
  </div>
</template>

<script>
export default {
  name: 'CyberTerminal',
  props: {
    title: {
      type: String,
      default: '对话终端'
    },
    status: {
      type: String,
      default: 'ONLINE'
    },
    messages: {
      type: Array,
      default: () => []
    },
    showInput: {
      type: Boolean,
      default: false
    },
    inputPlaceholder: {
      type: String,
      default: '输入消息...'
    },
    inputDisabled: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      inputValue: ''
    }
  },
  watch: {
    messages: {
      handler() {
        this.$nextTick(() => {
          if (this.$refs.screen) {
            this.$refs.screen.scrollTop = this.$refs.screen.scrollHeight;
          }
        });
      },
      deep: true,
      immediate: true
    }
  },
  methods: {
    formatTime(timestamp) {
      if (!timestamp) return '';
      const date = new Date(timestamp);
      return date.toLocaleTimeString('zh-CN', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      });
    },
    formatContent(content) {
      if (!content) return '';
      
      // 处理Markdown样式的代码块
      content = content.replace(/```([a-z]*)\n([\s\S]*?)\n```/g, '<pre class="code-block"><code>$2</code></pre>');
      
      // 处理换行符
      content = content.replace(/\n/g, '<br>');
      
      // 处理粗体文本
      content = content.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
      
      // 处理斜体文本
      content = content.replace(/\*(.*?)\*/g, '<em>$1</em>');
      
      return content;
    },
    sendMessage() {
      if (!this.inputValue.trim() || this.inputDisabled) return;
      
      this.$emit('send', this.inputValue);
      this.inputValue = '';
    },
    focusInput() {
      if (this.$refs.input) {
        this.$refs.input.focus();
      }
    }
  },
  mounted() {
    if (this.showInput && !this.inputDisabled) {
      this.focusInput();
    }
  }
}
</script>

<style scoped>
.cyber-terminal {
  background-color: var(--bg-darker);
  border: 1px solid var(--cyber-neon);
  box-shadow: 0 0 15px rgba(0, 255, 255, 0.2);
  position: relative;
  height: 500px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.cyber-terminal__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 1rem;
  background: linear-gradient(to right, var(--bg-dark), var(--bg-medium));
  border-bottom: 1px solid var(--cyber-neon);
}

.cyber-terminal__title {
  font-family: var(--font-display);
  color: var(--cyber-neon);
  text-transform: uppercase;
  letter-spacing: 1px;
  font-size: 0.9rem;
}

.cyber-terminal__status {
  display: flex;
  align-items: center;
  font-family: var(--font-mono);
  font-size: 0.7rem;
  color: var(--text-secondary);
}

.cyber-terminal__status-dot {
  width: 8px;
  height: 8px;
  background: var(--cyber-green);
  border-radius: 50%;
  margin-right: 5px;
  animation: pulse 2s infinite;
}

.cyber-terminal__controls {
  display: flex;
  gap: 5px;
}

.cyber-terminal__control {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  border: none;
  cursor: pointer;
}

.cyber-terminal__control--minimize {
  background: var(--cyber-yellow);
}

.cyber-terminal__control--maximize {
  background: var(--cyber-green);
}

.cyber-terminal__control--close {
  background: var(--cyber-pink);
}

.cyber-terminal__screen {
  flex: 1;
  padding: 1rem;
  overflow-y: auto;
  position: relative;
  font-family: var(--font-mono);
  font-size: 0.9rem;
  line-height: 1.5;
  color: var(--text-primary);
  background-color: rgba(10, 10, 15, 0.9);
}

.cyber-terminal__message {
  margin-bottom: 1rem;
  position: relative;
}

.cyber-terminal__message--system {
  color: var(--cyber-blue);
}

.cyber-terminal__message--error {
  color: var(--cyber-pink);
}

.cyber-terminal__message--user {
  color: var(--cyber-green);
}

.cyber-terminal__message--agent {
  color: var(--cyber-purple);
}

.cyber-terminal__message-header {
  margin-bottom: 0.3rem;
  display: flex;
  align-items: center;
  opacity: 0.7;
}

.cyber-terminal__message-timestamp {
  font-size: 0.7rem;
  margin-right: 0.5rem;
  color: var(--text-secondary);
}

.cyber-terminal__message-user {
  font-weight: bold;
  text-transform: uppercase;
}

.cyber-terminal__message-content {
  word-wrap: break-word;
  line-height: 1.6;
}

.cyber-terminal__message-content :deep(.code-block) {
  background: rgba(0, 0, 0, 0.3);
  padding: 0.5rem;
  margin: 0.5rem 0;
  border-left: 2px solid var(--cyber-blue);
  overflow-x: auto;
}

.cyber-terminal__scan-line {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 15px;
  background: linear-gradient(to bottom, 
    rgba(0, 255, 255, 0.15), 
    rgba(0, 255, 255, 0.05) 50%, 
    rgba(0, 255, 255, 0) 100%);
  z-index: 1;
  pointer-events: none;
  animation: scan 6s linear infinite;
}

@keyframes scan {
  0% {
    top: 0%;
  }
  100% {
    top: 100%;
  }
}

.cyber-terminal__input-area {
  display: flex;
  align-items: center;
  padding: 0.7rem 1rem;
  background-color: var(--bg-darker);
  border-top: 1px solid var(--cyber-neon);
}

.cyber-terminal__prompt {
  color: var(--cyber-green);
  margin-right: 0.5rem;
  font-family: var(--font-mono);
  font-weight: bold;
}

.cyber-terminal__input {
  flex: 1;
  background: transparent;
  border: none;
  color: var(--text-primary);
  font-family: var(--font-mono);
  font-size: 0.9rem;
  outline: none;
}

.cyber-terminal__loading {
  display: inline-flex;
  gap: 5px;
  margin-top: 0.3rem;
}

.cyber-terminal__loading .dot {
  width: 6px;
  height: 6px;
  background: currentColor;
  border-radius: 50%;
  animation: loading-dot 1.5s infinite;
}

.cyber-terminal__loading .dot:nth-child(2) {
  animation-delay: 0.2s;
}

.cyber-terminal__loading .dot:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes loading-dot {
  0%, 100% {
    opacity: 0.2;
  }
  50% {
    opacity: 1;
  }
}

@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(57, 255, 20, 0.7);
  }
  70% {
    box-shadow: 0 0 0 5px rgba(57, 255, 20, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(57, 255, 20, 0);
  }
}
</style> 