<template>
  <div class="cyber-editor-container">
    <div class="cyber-editor-header">
      <div class="cyber-editor-title">{{ title }}</div>
      <div class="cyber-editor-actions">
        <span class="cyber-editor-badge">{{ type.toUpperCase() }}</span>
        <span class="cyber-editor-line-count">行数: {{ lineCount }}</span>
      </div>
    </div>
    <div class="cyber-editor-wrapper">
      <textarea
        ref="editorTextarea"
        :value="modelValue"
        class="cyber-editor"
        :placeholder="placeholder"
        @input="updateContent"
        @scroll="handleScroll"
        :style="{ height: `${height}px` }"
      ></textarea>
      <div 
        class="cyber-editor-line-numbers" 
        ref="lineNumbers"
        :style="{ height: `${height}px` }"
      >
        <div v-for="n in lineCount" :key="n" class="line-number">{{ n }}</div>
      </div>
      <div class="cyber-editor-border cyber-editor-border-top"></div>
      <div class="cyber-editor-border cyber-editor-border-right"></div>
      <div class="cyber-editor-border cyber-editor-border-bottom"></div>
      <div class="cyber-editor-border cyber-editor-border-left"></div>
      <div class="cyber-editor-scanner"></div>
    </div>
    <div class="cyber-editor-footer">
      <slot name="footer"></slot>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CyberEditor',
  props: {
    modelValue: {
      type: String,
      default: ''
    },
    title: {
      type: String,
      default: '编辑器'
    },
    type: {
      type: String,
      default: 'text'
    },
    placeholder: {
      type: String,
      default: '在此输入...'
    },
    height: {
      type: Number,
      default: 300
    }
  },
  data() {
    return {
      lineCount: 1
    }
  },
  watch: {
    modelValue: {
      handler(val) {
        this.updateLineCount(val);
      },
      immediate: true
    }
  },
  methods: {
    updateContent(e) {
      this.$emit('update:modelValue', e.target.value);
      this.updateLineCount(e.target.value);
    },
    updateLineCount(text) {
      if (!text) {
        this.lineCount = 1;
        return;
      }
      this.lineCount = text.split('\n').length;
    },
    handleScroll() {
      if (this.$refs.lineNumbers) {
        this.$refs.lineNumbers.scrollTop = this.$refs.editorTextarea.scrollTop;
      }
    }
  }
}
</script>

<style scoped>
.cyber-editor-container {
  width: 100%;
  margin-bottom: 1.5rem;
  position: relative;
}

.cyber-editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 1rem;
  background: var(--bg-darker);
  border-bottom: 1px solid var(--cyber-neon);
  box-shadow: 0 0 5px var(--cyber-neon);
}

.cyber-editor-title {
  font-family: var(--font-display);
  text-transform: uppercase;
  color: var(--cyber-neon);
  letter-spacing: 1px;
}

.cyber-editor-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.cyber-editor-badge {
  background-color: var(--cyber-pink);
  color: var(--bg-darker);
  padding: 0.2rem 0.5rem;
  font-size: 0.7rem;
  font-family: var(--font-mono);
  border-radius: 2px;
}

.cyber-editor-line-count {
  font-family: var(--font-mono);
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.cyber-editor-wrapper {
  position: relative;
  display: flex;
  background: var(--bg-medium);
}

.cyber-editor {
  flex: 1;
  background: transparent;
  color: var(--text-primary);
  font-family: var(--font-mono);
  font-size: 0.9rem;
  line-height: 1.5;
  padding: 1rem 1rem 1rem 3.5rem;
  border: none;
  resize: none;
  outline: none;
  overflow-y: auto;
  white-space: pre;
  tab-size: 2;
  z-index: 2;
}

.cyber-editor-line-numbers {
  position: absolute;
  top: 0;
  left: 0;
  width: 2.5rem;
  background: var(--bg-darker);
  font-family: var(--font-mono);
  font-size: 0.85rem;
  line-height: 1.5;
  padding: 1rem 0.5rem;
  text-align: right;
  color: var(--text-secondary);
  overflow: hidden;
  user-select: none;
  border-right: 1px solid var(--cyber-blue);
  box-shadow: 2px 0 5px rgba(0, 191, 255, 0.2);
  z-index: 1;
}

.cyber-editor-border {
  position: absolute;
  background: var(--cyber-neon);
  z-index: 3;
  opacity: 0.7;
}

.cyber-editor-border-top {
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  box-shadow: 0 0 5px var(--cyber-neon);
}

.cyber-editor-border-right {
  top: 0;
  right: 0;
  bottom: 0;
  width: 1px;
  box-shadow: 0 0 5px var(--cyber-neon);
}

.cyber-editor-border-bottom {
  bottom: 0;
  left: 0;
  right: 0;
  height: 1px;
  box-shadow: 0 0 5px var(--cyber-neon);
}

.cyber-editor-border-left {
  top: 0;
  left: 0;
  bottom: 0;
  width: 1px;
  box-shadow: 0 0 5px var(--cyber-neon);
}

.cyber-editor-scanner {
  position: absolute;
  height: 2px;
  left: 0;
  right: 0;
  background: linear-gradient(to right, transparent, var(--cyber-neon), transparent);
  animation: scan 3s linear infinite;
  opacity: 0.5;
  z-index: 2;
}

@keyframes scan {
  0% {
    top: 0;
  }
  100% {
    top: 100%;
  }
}

.cyber-editor::placeholder {
  color: var(--text-disabled);
}

.cyber-editor-footer {
  padding: 0.5rem 1rem;
  background: var(--bg-darker);
  border-top: 1px solid var(--cyber-blue);
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
}
</style> 