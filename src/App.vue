<template>
  <div class="app" :class="{'light-mode': !isDarkMode}">
    <header class="app-header">
      <div class="header-content">
        <div class="logo">
          <router-link to="/" class="logo-text">JADE<span class="logo-highlight">Agent</span></router-link>
        </div>
        
        <nav class="main-nav">
          <router-link to="/" class="nav-link" exact>首页</router-link>
          <router-link to="/agents" class="nav-link">智能体</router-link>
          <router-link to="/market" class="nav-link">市场</router-link>
        </nav>
        
        <div class="header-controls">
          <button @click="toggleTheme" class="theme-toggle-btn">
            <span v-if="isDarkMode" class="theme-icon">🌙</span>
            <span v-else class="theme-icon">☀️</span>
          </button>
          
          <WalletConnect class="wallet-connect-component" simplified />
          
          <button class="create-button" @click="navigateToCreate">
            <span class="plus-icon">+</span>
            <span class="button-text">创建智能体</span>
          </button>
        </div>
      </div>
    </header>
    
    <main class="app-content">
      <router-view />
    </main>
    
    <footer class="app-footer">
      <div class="footer-content">
        <div class="footer-section">
          <div class="footer-title">JADE Agent</div>
          <div class="footer-description">
            基于Efficode协议的智能体网络
          </div>
        </div>
        
        <div class="footer-section links">
          <a href="#" class="footer-link">关于我们</a>
          <a href="#" class="footer-link">使用文档</a>
          <a href="#" class="footer-link">API</a>
          <a href="#" class="footer-link">社区</a>
        </div>
        
        <div class="footer-section">
          <div class="footer-protocol">
            <div class="protocol-title">Efficode协议</div>
            <div class="protocol-version">500字节压缩阈值</div>
          </div>
        </div>
      </div>
      
      <div class="footer-copyright">
        © 2023 JADE Agent · <span class="highlight">智能体自由通信的未来</span>
      </div>
    </footer>
    
    <!-- 添加移动端导航 -->
    <nav class="mobile-nav">
      <router-link to="/" class="mobile-nav-link" exact>
        <span class="mobile-nav-icon">🏠</span>
        <span>首页</span>
      </router-link>
      <router-link to="/agents" class="mobile-nav-link">
        <span class="mobile-nav-icon">🤖</span>
        <span>智能体</span>
      </router-link>
      <router-link to="/market" class="mobile-nav-link">
        <span class="mobile-nav-icon">📈</span>
        <span>市场</span>
      </router-link>
      <router-link to="/agent/create" class="mobile-nav-link">
        <span class="mobile-nav-icon">➕</span>
        <span>创建</span>
      </router-link>
    </nav>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import WalletConnect from '@/components/WalletConnect.vue';
import blockchainService from '@/services/blockchain';

const router = useRouter();
const isDarkMode = ref(true); // 默认为暗色模式

// 区块链状态
const blockchainConnected = ref(false);
const blockchainAccount = ref('');
const blockchainBalance = ref('0');
const blockchainCurrency = ref('BNB');
const showBlockchainMenu = ref(false);
const selectedChain = ref('bnb-chain');

// 初始化
onMounted(async () => {
  // 初始化区块链服务
  await blockchainService.initialize();
  updateBlockchainStatus();
  
  // 检查本地存储中的主题偏好
  const savedTheme = localStorage.getItem('theme');
  if (savedTheme) {
    isDarkMode.value = savedTheme === 'dark';
  }
  
  // 监听点击事件，用于关闭区块链菜单
  document.addEventListener('click', (event) => {
    const target = event.target;
    const blockchainMenu = document.querySelector('.blockchain-menu');
    const blockchainStatus = document.querySelector('.blockchain-status');
    
    if (blockchainMenu && !blockchainMenu.contains(target) && !blockchainStatus.contains(target)) {
      showBlockchainMenu.value = false;
    }
  });
});

// 监听主题变化并保存到本地存储
watch(isDarkMode, (newValue) => {
  localStorage.setItem('theme', newValue ? 'dark' : 'light');
});

// 切换主题
const toggleTheme = () => {
  isDarkMode.value = !isDarkMode.value;
};

// 更新区块链状态
const updateBlockchainStatus = () => {
  const status = blockchainService.getConnectionStatus();
  blockchainConnected.value = status.connected;
  blockchainAccount.value = status.account || '';
  blockchainBalance.value = status.balance || '0';
  blockchainCurrency.value = status.currency || 'BNB';
  selectedChain.value = status.chain || 'bnb-chain';
};

// 切换区块链菜单显示
const toggleBlockchainMenu = () => {
  showBlockchainMenu.value = !showBlockchainMenu.value;
};

// 连接钱包
const connectWallet = async () => {
  try {
    await blockchainService.connectWallet();
    updateBlockchainStatus();
    showBlockchainMenu.value = false;
  } catch (error) {
    console.error('连接钱包失败:', error);
  }
};

// 断开钱包连接
const disconnectWallet = async () => {
  try {
    await blockchainService.disconnectWallet();
    updateBlockchainStatus();
    showBlockchainMenu.value = false;
  } catch (error) {
    console.error('断开钱包连接失败:', error);
  }
};

// 导航到创建智能体页面
const navigateToCreate = () => {
  router.push('/agent/create');
};
</script>

<style>
/* 全局样式 */
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;500;600;700&family=Share+Tech+Mono&display=swap');

:root {
  /* 暗色模式变量 */
  --dark-primary-color: #00ff00;
  --dark-bg-color: #0a0a0a;
  --dark-text-color: #ffffff;
  --dark-secondary-color: rgba(255, 255, 255, 0.6);
  --dark-bg-lighter: rgba(30, 30, 40, 0.8);
  --dark-border-color: rgba(0, 255, 234, 0.3);
  --dark-accent-color: rgba(0, 255, 234, 0.8);
  --dark-text-shadow: 0 0 10px rgba(0, 255, 0, 0.5);
  --dark-input-bg: rgba(0, 0, 0, 0.3);
  --dark-input-text: #ffffff;
  
  /* 浅色模式变量 - 更新为米奇色 */
  --light-primary-color: #006633; /* 墨绿色 */
  --light-bg-color: #f9f3e6; /* 米奇色浅色背景 */
  --light-text-color: #333333;
  --light-secondary-color: rgba(0, 0, 0, 0.6);
  --light-bg-lighter: rgba(251, 246, 232, 0.8); /* 更浅的米奇色 */
  --light-border-color: rgba(0, 102, 51, 0.5); /* 深绿色边框 */
  --light-accent-color: rgba(0, 153, 102, 0.8);
  --light-text-shadow: none; /* 无文字阴影 */
  --light-input-bg: rgba(249, 243, 230, 0.8); /* 米奇色输入框背景 */
  --light-input-text: #333333; /* 黑色文字 */
  
  /* 默认使用暗色模式 */
  --primary-color: var(--dark-primary-color);
  --bg-color: var(--dark-bg-color);
  --text-color: var(--dark-text-color);
  --text-secondary: var(--dark-secondary-color);
  --bg-lighter: var(--dark-bg-lighter);
  --border-color: var(--dark-border-color);
  --accent-color: var(--dark-accent-color);
  --text-shadow: var(--dark-text-shadow);
  --input-bg: var(--dark-input-bg);
  --input-text: var(--dark-input-text);
}

/* 浅色模式 */
.light-mode {
  --primary-color: var(--light-primary-color);
  --bg-color: var(--light-bg-color);
  --text-color: var(--light-text-color);
  --text-secondary: var(--light-secondary-color);
  --bg-lighter: var(--light-bg-lighter);
  --border-color: var(--light-border-color);
  --accent-color: var(--light-accent-color);
  --text-shadow: var(--light-text-shadow);
  --input-bg: var(--light-input-bg);
  --input-text: var(--light-input-text);
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen,
    Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
  background-color: var(--bg-color);
  color: var(--text-color);
  line-height: 1.6;
}

a {
  color: inherit;
  text-decoration: none;
}

button {
  background: none;
  border: none;
  font-family: 'Rajdhani', sans-serif;
  cursor: pointer;
}

.app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: var(--bg-color);
  transition: background-color 0.3s ease;
}

/* 头部样式 */
.app-header {
  background-color: var(--bg-lighter);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid var(--border-color);
  position: sticky;
  top: 0;
  z-index: 100;
  transition: all 0.3s ease;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1200px;
  margin: 0 auto;
  padding: 15px 20px;
}

.logo {
  display: flex;
  flex-direction: column;
  min-width: 180px;
}

.logo-text {
  font-size: 24px;
  font-weight: 700;
  letter-spacing: 1px;
  color: var(--text-color);
  transition: color 0.3s ease;
}

.logo-highlight {
  color: var(--primary-color);
  position: relative;
  transition: color 0.3s ease;
}

.main-nav {
  display: flex;
  gap: 40px;
  justify-content: center;
  width: 400px;
  margin: 0 auto;
}

.nav-link {
  color: var(--text-secondary);
  font-size: 16px;
  text-transform: uppercase;
  letter-spacing: 1px;
  transition: all 0.3s ease;
  position: relative;
  padding: 5px 0;
}

.nav-link:hover,
.nav-link.router-link-active {
  color: var(--primary-color);
}

.nav-link::after {
  content: '';
  position: absolute;
  bottom: -5px;
  left: 0;
  width: 0;
  height: 2px;
  background-color: var(--primary-color);
  transition: width 0.3s;
}

.nav-link:hover::after,
.nav-link.router-link-active::after {
  width: 100%;
}

.header-controls {
  display: flex;
  align-items: center;
  gap: 15px;
  min-width: 180px;
  justify-content: flex-end;
}

/* 主题切换按钮 */
.theme-toggle-btn {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 50%;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  border: 1px solid var(--border-color);
}

.theme-toggle-btn:hover {
  transform: scale(1.05);
  box-shadow: 0 0 10px rgba(0, 255, 0, 0.2);
}

.theme-icon {
  font-size: 20px;
}

.light-mode .theme-toggle-btn {
  background: rgba(240, 240, 245, 0.8);
}

.create-button {
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(0, 255, 0, 0.1);
  color: var(--primary-color);
  border: 1px solid var(--border-color);
  padding: 8px 16px;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.3s ease;
  text-shadow: var(--text-shadow);
}

.create-button:hover {
  background: rgba(0, 255, 0, 0.2);
  border-color: var(--primary-color);
  box-shadow: 0 0 15px rgba(0, 255, 0, 0.3);
}

.light-mode .create-button {
  background: rgba(0, 102, 51, 0.1);
}

.light-mode .create-button:hover {
  background: rgba(0, 102, 51, 0.2);
  box-shadow: 0 0 15px rgba(0, 102, 51, 0.3);
}

.plus-icon {
  font-size: 18px;
  font-weight: 400;
}

/* 内容样式 */
.app-content {
  flex: 1;
  transition: background-color 0.3s ease;
}

/* 页脚样式 */
.app-footer {
  background-color: var(--bg-lighter);
  border-top: 1px solid var(--border-color);
  padding: 40px 20px 20px;
  margin-top: auto;
  transition: all 0.3s ease;
}

.footer-content {
  display: flex;
  justify-content: space-between;
  flex-wrap: wrap;
  max-width: 1200px;
  margin: 0 auto;
  padding-bottom: 30px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.light-mode .footer-content {
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
}

.footer-section {
  max-width: 300px;
  margin-bottom: 20px;
}

.footer-title {
  color: var(--primary-color);
  font-size: 20px;
  font-weight: 600;
  margin-bottom: 10px;
  transition: color 0.3s ease;
}

.footer-description {
  color: var(--text-secondary);
  font-size: 14px;
  line-height: 1.6;
  transition: color 0.3s ease;
}

.footer-section.links {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
}

.footer-link {
  color: var(--text-secondary);
  font-size: 14px;
  transition: color 0.3s ease;
}

.footer-link:hover {
  color: var(--primary-color);
}

.protocol-title {
  color: var(--primary-color);
  font-size: 16px;
  margin-bottom: 5px;
  transition: color 0.3s ease;
}

.protocol-version {
  color: var(--text-secondary);
  font-size: 14px;
  transition: color 0.3s ease;
}

.footer-copyright {
  max-width: 1200px;
  margin: 20px auto 0;
  text-align: center;
  color: var(--text-secondary);
  font-size: 14px;
  transition: color 0.3s ease;
}

.highlight {
  color: var(--primary-color);
  transition: color 0.3s ease;
}

/* 移动设备底部导航栏 */
@media (max-width: 768px) {
  .app-footer {
    padding-bottom: 80px; /* 为底部导航留出空间 */
  }
  
  .mobile-nav {
    display: flex;
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background-color: var(--bg-lighter);
    backdrop-filter: blur(10px);
    border-top: 1px solid var(--border-color);
    z-index: 100;
    transition: all 0.3s ease;
  }
  
  .mobile-nav-link {
    flex: 1;
    text-align: center;
    padding: 12px 0;
    font-size: 12px;
    color: var(--text-secondary);
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 5px;
    transition: color 0.3s ease;
  }
  
  .mobile-nav-link.router-link-active {
    color: var(--primary-color);
  }
  
  .mobile-nav-icon {
    font-size: 20px;
  }
  
  /* 隐藏桌面导航 */
  .main-nav {
    display: none;
  }
  
  .header-content {
    flex-direction: column;
  }
  
  .logo {
    margin-bottom: 10px;
  }
}

/* 桌面版隐藏移动导航 */
@media (min-width: 769px) {
  .mobile-nav {
    display: none;
  }
}

/* 钱包连接组件样式 */
.wallet-connect-component {
  max-width: 40px;
  min-width: 40px;
  padding: 0 !important;
  margin: 0 !important;
  border: none !important;
  background: transparent !important;
}

@media (max-width: 768px) {
  .wallet-connect-component {
    max-width: 100%;
    margin: 0 0 1rem 0 !important;
    padding: 0.5rem !important;
    background: rgba(0, 0, 0, 0.3) !important;
    border: 1px solid rgba(0, 255, 0, 0.2) !important;
  }
  
  .light-mode .wallet-connect-component {
    background: rgba(240, 240, 245, 0.8) !important;
    border: 1px solid rgba(0, 153, 0, 0.2) !important;
  }
  
  .header-controls {
    flex-direction: column;
    align-items: stretch;
    width: 100%;
    min-width: auto;
    gap: 10px;
  }
  
  .theme-toggle-btn {
    align-self: center;
  }
}

h1, h2, h3, h4, h5, h6 {
  color: var(--primary-color);
  text-shadow: var(--text-shadow);
  font-weight: 600;
  margin-bottom: 0.5rem;
  line-height: 1.2;
}

input, textarea, select {
  background-color: var(--input-bg);
  color: var(--input-text);
  border: 1px solid var(--border-color);
  padding: 0.5rem;
  border-radius: 4px;
  font-size: 1rem;
}

input:focus, textarea:focus, select:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 5px rgba(var(--primary-color), 0.3);
}
</style> 