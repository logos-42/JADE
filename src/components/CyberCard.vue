<template>
  <div 
    :class="['cyber-card', { 'cyber-card--highlight': highlight, 'cyber-card--selectable': selectable }]"
    @click="handleClick"
  >
    <div class="cyber-card__glitch-layer" v-if="glitch"></div>
    <div class="cyber-card__corner cyber-card__corner--tl"></div>
    <div class="cyber-card__corner cyber-card__corner--tr"></div>
    <div class="cyber-card__corner cyber-card__corner--bl"></div>
    <div class="cyber-card__corner cyber-card__corner--br"></div>
    <div class="cyber-card__header" v-if="$slots.header || title">
      <slot name="header">
        <div class="cyber-card__title">{{ title }}</div>
      </slot>
    </div>
    <div class="cyber-card__body">
      <slot></slot>
    </div>
    <div class="cyber-card__footer" v-if="$slots.footer">
      <slot name="footer"></slot>
    </div>
    <div class="cyber-card__border cyber-card__border--top"></div>
    <div class="cyber-card__border cyber-card__border--right"></div>
    <div class="cyber-card__border cyber-card__border--bottom"></div>
    <div class="cyber-card__border cyber-card__border--left"></div>
  </div>
</template>

<script>
export default {
  name: 'CyberCard',
  props: {
    title: {
      type: String,
      default: ''
    },
    highlight: {
      type: Boolean,
      default: false
    },
    glitch: {
      type: Boolean,
      default: false
    },
    selectable: {
      type: Boolean,
      default: false
    }
  },
  methods: {
    handleClick(event) {
      if (this.selectable) {
        this.$emit('click', event);
      }
    }
  }
}
</script>

<style scoped>
.cyber-card {
  background-color: var(--bg-medium);
  position: relative;
  margin: 1rem 0;
  overflow: hidden;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.cyber-card__corner {
  position: absolute;
  width: 15px;
  height: 15px;
  z-index: 2;
}

.cyber-card__corner--tl {
  top: 0;
  left: 0;
  border-top: 2px solid var(--cyber-blue);
  border-left: 2px solid var(--cyber-blue);
}

.cyber-card__corner--tr {
  top: 0;
  right: 0;
  border-top: 2px solid var(--cyber-blue);
  border-right: 2px solid var(--cyber-blue);
}

.cyber-card__corner--bl {
  bottom: 0;
  left: 0;
  border-bottom: 2px solid var(--cyber-blue);
  border-left: 2px solid var(--cyber-blue);
}

.cyber-card__corner--br {
  bottom: 0;
  right: 0;
  border-bottom: 2px solid var(--cyber-blue);
  border-right: 2px solid var(--cyber-blue);
}

.cyber-card__header {
  padding: 1rem;
  border-bottom: 1px solid var(--cyber-blue);
  position: relative;
  z-index: 1;
}

.cyber-card__title {
  font-family: var(--font-display);
  color: var(--cyber-blue);
  text-transform: uppercase;
  letter-spacing: 1px;
  font-size: 1.1rem;
  font-weight: 600;
  text-shadow: 0 0 5px var(--cyber-blue);
}

.cyber-card__body {
  padding: 1rem;
  position: relative;
  z-index: 1;
}

.cyber-card__footer {
  padding: 1rem;
  border-top: 1px solid var(--cyber-blue);
  position: relative;
  z-index: 1;
}

.cyber-card__border {
  position: absolute;
  background: var(--cyber-blue);
  z-index: 0;
  transition: all 0.3s ease;
}

.cyber-card__border--top {
  top: 0;
  left: 15px;
  right: 15px;
  height: 1px;
}

.cyber-card__border--right {
  top: 15px;
  right: 0;
  bottom: 15px;
  width: 1px;
}

.cyber-card__border--bottom {
  bottom: 0;
  left: 15px;
  right: 15px;
  height: 1px;
}

.cyber-card__border--left {
  top: 15px;
  left: 0;
  bottom: 15px;
  width: 1px;
}

.cyber-card--highlight {
  box-shadow: 0 0 15px var(--cyber-neon);
}

.cyber-card--highlight .cyber-card__corner {
  border-color: var(--cyber-neon);
}

.cyber-card--highlight .cyber-card__border {
  background: var(--cyber-neon);
}

.cyber-card--highlight .cyber-card__title {
  color: var(--cyber-neon);
  text-shadow: 0 0 5px var(--cyber-neon);
}

.cyber-card--selectable {
  cursor: pointer;
}

.cyber-card--selectable:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0, 191, 255, 0.3);
}

.cyber-card__glitch-layer {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(45deg, transparent 65%, rgba(0, 191, 255, 0.1) 70%, transparent 75%);
  background-size: 200% 200%;
  animation: cyber-card-glitch 3s linear infinite;
  pointer-events: none;
  z-index: 1;
}

@keyframes cyber-card-glitch {
  0% {
    background-position: 0% 0%;
  }
  100% {
    background-position: 200% 200%;
  }
}
</style> 