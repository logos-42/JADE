<template>
  <button 
    :class="['cyber-button', `cyber-button--${type}`, { 'cyber-button--glitch': glitch }]" 
    :disabled="disabled"
    @click="$emit('click')"
  >
    <div class="cyber-button__glitch" v-if="glitch"></div>
    <span class="cyber-button__content">
      <slot></slot>
    </span>
  </button>
</template>

<script>
export default {
  name: 'CyberButton',
  props: {
    type: {
      type: String,
      default: 'primary',
      validator: (value) => ['primary', 'secondary', 'danger', 'success', 'warning'].includes(value)
    },
    disabled: {
      type: Boolean,
      default: false
    },
    glitch: {
      type: Boolean,
      default: false
    }
  },
  emits: ['click']
}
</script>

<style scoped>
.cyber-button {
  position: relative;
  background-color: transparent;
  color: var(--text-primary);
  font-family: var(--font-display);
  text-transform: uppercase;
  letter-spacing: 2px;
  font-size: 0.9rem;
  padding: 0.8rem 1.6rem;
  border: 1px solid;
  cursor: pointer;
  transition: all 0.2s ease;
  overflow: hidden;
  margin: 0.5rem 0;
  clip-path: polygon(
    0 0, 
    calc(100% - 8px) 0, 
    100% 8px, 
    100% calc(100% - 0px), 
    calc(100% - 0px) 100%, 
    8px 100%, 
    0 calc(100% - 8px)
  );
}

.cyber-button::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(to right, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: all 0.5s ease;
}

.cyber-button:hover::before {
  left: 100%;
}

.cyber-button--primary {
  border-color: var(--cyber-neon);
  color: var(--cyber-neon);
  box-shadow: 0 0 5px var(--cyber-neon);
}

.cyber-button--primary:hover {
  background-color: rgba(0, 255, 255, 0.1);
  box-shadow: 0 0 10px var(--cyber-neon);
}

.cyber-button--secondary {
  border-color: var(--cyber-purple);
  color: var(--cyber-purple);
  box-shadow: 0 0 5px var(--cyber-purple);
}

.cyber-button--secondary:hover {
  background-color: rgba(148, 0, 211, 0.1);
  box-shadow: 0 0 10px var(--cyber-purple);
}

.cyber-button--danger {
  border-color: var(--cyber-pink);
  color: var(--cyber-pink);
  box-shadow: 0 0 5px var(--cyber-pink);
}

.cyber-button--danger:hover {
  background-color: rgba(240, 50, 140, 0.1);
  box-shadow: 0 0 10px var(--cyber-pink);
}

.cyber-button--success {
  border-color: var(--cyber-green);
  color: var(--cyber-green);
  box-shadow: 0 0 5px var(--cyber-green);
}

.cyber-button--success:hover {
  background-color: rgba(57, 255, 20, 0.1);
  box-shadow: 0 0 10px var(--cyber-green);
}

.cyber-button--warning {
  border-color: var(--cyber-yellow);
  color: var(--cyber-yellow);
  box-shadow: 0 0 5px var(--cyber-yellow);
}

.cyber-button--warning:hover {
  background-color: rgba(246, 250, 112, 0.1);
  box-shadow: 0 0 10px var(--cyber-yellow);
}

.cyber-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.cyber-button:disabled::before {
  display: none;
}

.cyber-button--glitch {
  position: relative;
}

.cyber-button__glitch {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: currentColor;
  opacity: 0.1;
  animation: glitch-animation 2s infinite;
  z-index: -1;
}

@keyframes glitch-animation {
  0% {
    transform: translate(0);
  }
  20% {
    transform: translate(-5px, 5px);
  }
  40% {
    transform: translate(-5px, -5px);
  }
  60% {
    transform: translate(5px, 5px);
  }
  80% {
    transform: translate(5px, -5px);
  }
  100% {
    transform: translate(0);
  }
}
</style> 