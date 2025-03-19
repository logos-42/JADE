<template>
  <div class="home">
    <h1>JADE</h1>
    <p class="description">边缘智能体网络——基于ANP/MCP协议的NFT算力革命</p>
    <div class="actions">
      <router-link to="/agents" class="action-btn">
        查看智能体列表
      </router-link>
    </div>
  </div>
</template>

<script setup>
// 首页组件逻辑
</script>

<style scoped>
.home {
  padding: 2rem;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 70vh;
}

h1 {
  font-size: 3.5rem;
  margin-bottom: 1rem;
  color: var(--primary-color);
  text-shadow: var(--text-shadow);
}

.description {
  font-size: 1.2rem;
  color: var(--text-color);
  margin-bottom: 2rem;
  max-width: 600px;
}

.actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
}

.action-btn {
  padding: 0.8rem 1.5rem;
  background: rgba(0, 255, 0, 0.1);
  border: 1px solid var(--primary-color);
  color: var(--primary-color);
  text-decoration: none;
  border-radius: 4px;
  transition: all 0.3s ease;
  font-size: 1.1rem;
}

.light-mode .action-btn {
  background: rgba(0, 102, 51, 0.05);
}

.action-btn:hover {
  background: rgba(0, 255, 0, 0.2);
  box-shadow: 0 0 15px rgba(0, 255, 0, 0.3);
  transform: translateY(-3px);
}

.light-mode .action-btn:hover {
  background: rgba(0, 102, 51, 0.1);
  box-shadow: 0 0 15px rgba(0, 102, 51, 0.3);
}
</style> 