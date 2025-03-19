<template>
  <div class="cyber-input-container">
    <label v-if="label" :for="id" class="cyber-label">{{ label }}</label>
    <div class="cyber-input-wrapper">
      <input 
        :id="id"
        :type="type"
        :value="modelValue"
        :placeholder="placeholder"
        :disabled="disabled"
        :class="['cyber-input', { 'cyber-input--error': error }]"
        @input="$emit('update:modelValue', $event.target.value)"
      />
      <div class="cyber-input__border-top"></div>
      <div class="cyber-input__border-bottom"></div>
      <div class="cyber-input__border-left"></div>
      <div class="cyber-input__border-right"></div>
    </div>
    <div v-if="error" class="cyber-input-error">{{ error }}</div>
  </div>
</template>

<script>
export default {
  name: 'CyberInput',
  props: {
    id: {
      type: String,
      default() {
        return `cyber-input-${Math.random().toString(36).substr(2, 9)}`;
      }
    },
    modelValue: {
      type: [String, Number],
      default: ''
    },
    label: {
      type: String,
      default: ''
    },
    placeholder: {
      type: String,
      default: ''
    },
    type: {
      type: String,
      default: 'text'
    },
    error: {
      type: String,
      default: ''
    },
    disabled: {
      type: Boolean,
      default: false
    }
  },
  emits: ['update:modelValue']
}
</script>

<style scoped>
.cyber-input-container {
  margin-bottom: 1.5rem;
  width: 100%;
}

.cyber-label {
  display: block;
  margin-bottom: 0.5rem;
  font-family: var(--font-mono);
  color: var(--text-secondary);
  text-transform: uppercase;
  font-size: 0.8rem;
  letter-spacing: 1px;
}

.cyber-input-wrapper {
  position: relative;
  width: 100%;
}

.cyber-input {
  width: 100%;
  padding: 0.9rem 1rem;
  background-color: var(--bg-medium);
  color: var(--text-primary);
  font-family: var(--font-mono);
  border: none;
  font-size: 1rem;
  transition: all 0.3s ease;
  outline: none;
  z-index: 1;
  position: relative;
  box-sizing: border-box;
}

.cyber-input:focus {
  background-color: var(--bg-light);
}

.cyber-input::placeholder {
  color: var(--text-disabled);
}

.cyber-input:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.cyber-input__border-top,
.cyber-input__border-bottom,
.cyber-input__border-left,
.cyber-input__border-right {
  position: absolute;
  background: var(--cyber-neon);
  transition: all 0.2s ease;
}

.cyber-input__border-top,
.cyber-input__border-bottom {
  height: 2px;
  width: 0;
}

.cyber-input__border-left,
.cyber-input__border-right {
  width: 2px;
  height: 0;
}

.cyber-input__border-top {
  top: 0;
  left: 0;
}

.cyber-input__border-bottom {
  bottom: 0;
  right: 0;
}

.cyber-input__border-left {
  bottom: 0;
  left: 0;
}

.cyber-input__border-right {
  top: 0;
  right: 0;
}

.cyber-input-wrapper:hover .cyber-input__border-top,
.cyber-input-wrapper:hover .cyber-input__border-bottom,
.cyber-input:focus ~ .cyber-input__border-top,
.cyber-input:focus ~ .cyber-input__border-bottom {
  width: 100%;
}

.cyber-input-wrapper:hover .cyber-input__border-left,
.cyber-input-wrapper:hover .cyber-input__border-right,
.cyber-input:focus ~ .cyber-input__border-left,
.cyber-input:focus ~ .cyber-input__border-right {
  height: 100%;
}

.cyber-input--error {
  border: 1px solid var(--cyber-pink);
}

.cyber-input--error ~ .cyber-input__border-top,
.cyber-input--error ~ .cyber-input__border-bottom,
.cyber-input--error ~ .cyber-input__border-left,
.cyber-input--error ~ .cyber-input__border-right {
  background: var(--cyber-pink);
}

.cyber-input-error {
  color: var(--cyber-pink);
  font-size: 0.8rem;
  margin-top: 0.5rem;
  animation: error-pulse 1.5s infinite;
}

@keyframes error-pulse {
  0% {
    opacity: 0.7;
  }
  50% {
    opacity: 1;
  }
  100% {
    opacity: 0.7;
  }
}
</style> 