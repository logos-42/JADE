<template>
  <div class="wallet-connect">
    <!-- 未连接状态 -->
    <div v-if="!isConnected" class="connect-container">
      <button @click="connectWallet" class="connect-btn" :disabled="connecting">
        <img src="/metamask-logo.svg" alt="MetaMask" class="wallet-icon" v-if="isMetaMaskAvailable">
        {{ connecting ? '连接中...' : '连接MetaMask钱包' }}
      </button>
      <div v-if="!isMetaMaskAvailable" class="wallet-warning">
        您需要安装 <a href="https://metamask.io/download/" target="_blank">MetaMask</a> 插件
      </div>
    </div>
    
    <!-- 已连接状态 - 简洁模式（仅显示头像） -->
    <div v-else-if="isConnected && simplified" class="wallet-simplified" @click="toggleWalletDetails">
      <div class="wallet-avatar">
        <img src="/metamask-logo.svg" alt="MetaMask" class="wallet-avatar-icon">
        <span class="wallet-status-dot"></span>
      </div>
    </div>
    
    <!-- 已连接状态 - 详细模式 -->
    <div v-else class="wallet-info" @click="toggleWalletDetails">
      <div class="account-info">
        <div class="address">
          {{ formatAddress(account) }}
          <button @click.stop="copyAddress" class="copy-btn" title="复制地址">
            <i class="copy-icon">📋</i>
          </button>
        </div>
        <div class="balance">
          {{ balance }} {{ currency }}
        </div>
      </div>
      <button @click.stop="disconnectWallet" class="disconnect-btn">
        断开连接
      </button>
    </div>
    
    <!-- 钱包详情弹出框 -->
    <div v-if="showDetails" class="wallet-details-popup">
      <div class="wallet-details-header">
        <h3>钱包详情</h3>
        <button @click="showDetails = false" class="close-btn">×</button>
      </div>
      <div class="wallet-details-content">
        <div class="wallet-details-avatar">
          <img src="/metamask-logo.svg" alt="MetaMask" class="wallet-details-icon">
        </div>
        <div class="wallet-details-info">
          <div class="details-item">
            <label>钱包地址</label>
            <div class="details-address">
              {{ account }}
              <button @click="copyAddress" class="copy-details-btn" title="复制地址">
                <i class="copy-icon">📋</i>
              </button>
            </div>
          </div>
          <div class="details-item">
            <label>余额</label>
            <div class="details-balance">{{ balance }} {{ currency }}</div>
          </div>
          <div class="details-item">
            <label>链</label>
            <div class="details-network">{{ networkName }}</div>
          </div>
        </div>
        <div class="wallet-details-actions">
          <button @click="disconnectWallet" class="details-disconnect-btn">断开连接</button>
        </div>
      </div>
    </div>
    
    <!-- 错误提示 -->
    <div v-if="error" class="error-message">
      {{ error }}
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watchEffect } from 'vue';
import blockchainService from '../services/blockchain';

// 状态
const isConnected = ref(false);
const isMetaMaskAvailable = ref(false);
const account = ref('');
const balance = ref('0');
const currency = ref('ETH');
const connecting = ref(false);
const error = ref('');
const showDetails = ref(false);
const networkName = ref('以太坊主网');

// Props
const props = defineProps({
  // 是否使用简化模式（仅显示图标）
  simplified: {
    type: Boolean,
    default: false
  }
});

// 初始化
onMounted(async () => {
  try {
    // 初始化区块链服务
    await blockchainService.initialize();
    
    // 检查MetaMask是否可用
    isMetaMaskAvailable.value = typeof window !== 'undefined' && 
                               typeof window.ethereum !== 'undefined' && 
                               window.ethereum.isMetaMask;
    
    // 获取连接状态
    updateConnectionStatus();
    
    // 设置事件监听
    if (isMetaMaskAvailable.value) {
      window.ethereum.on('accountsChanged', handleAccountsChanged);
      window.ethereum.on('chainChanged', () => window.location.reload());
    }
  } catch (err) {
    error.value = '初始化钱包连接失败: ' + err.message;
  }
});

// 更新连接状态
const updateConnectionStatus = () => {
  const status = blockchainService.getConnectionStatus();
  isConnected.value = status.connected;
  account.value = status.account;
  balance.value = status.balance;
  currency.value = status.currency;
  
  // 设置网络名称
  switch (status.chain) {
    case 'bnb-chain':
      networkName.value = '币安智能链';
      break;
    case 'base':
      networkName.value = 'Base';
      break;
    case 'test':
      networkName.value = '测试网络';
      break;
    default:
      networkName.value = '以太坊主网';
  }
};

// 处理账户变更
const handleAccountsChanged = (accounts) => {
  if (accounts.length === 0) {
    // 用户在MetaMask中断开了连接
    isConnected.value = false;
    account.value = '';
    balance.value = '0';
  } else {
    // 用户切换了账户
    account.value = accounts[0];
    updateConnectionStatus();
  }
};

// 连接钱包
const connectWallet = async () => {
  if (!isMetaMaskAvailable.value) {
    error.value = '请先安装MetaMask插件';
    return;
  }
  
  connecting.value = true;
  error.value = '';
  
  try {
    const result = await blockchainService.connectWallet();
    if (result.success) {
      updateConnectionStatus();
      console.log('钱包连接成功:', result.account);
      
      // 发出钱包连接事件
      emit('wallet-connected', {
        account: account.value,
        balance: balance.value,
        currency: currency.value
      });
    } else {
      error.value = result.error || '连接钱包失败';
    }
  } catch (err) {
    error.value = '连接钱包时出错: ' + err.message;
  } finally {
    connecting.value = false;
  }
};

// 断开钱包连接
const disconnectWallet = async () => {
  try {
    const result = await blockchainService.disconnectWallet();
    if (result.success) {
      updateConnectionStatus();
      // 发出钱包断开连接事件
      emit('wallet-disconnected');
      // 关闭详情弹窗
      showDetails.value = false;
    } else {
      error.value = result.error || '断开连接失败';
    }
  } catch (err) {
    error.value = '断开连接时出错: ' + err.message;
  }
};

// 复制地址到剪贴板
const copyAddress = () => {
  if (account.value) {
    navigator.clipboard.writeText(account.value)
      .then(() => {
        alert('地址已复制到剪贴板');
      })
      .catch(err => {
        error.value = '复制地址失败: ' + err.message;
      });
  }
};

// 格式化地址显示
const formatAddress = (address) => {
  if (!address) return '';
  return address.slice(0, 6) + '...' + address.slice(-4);
};

// 切换钱包详情显示
const toggleWalletDetails = () => {
  showDetails.value = !showDetails.value;
};

// 定义事件
const emit = defineEmits(['wallet-connected', 'wallet-disconnected']);
</script>

<style scoped>
.wallet-connect {
  position: relative;
  background: rgba(0, 0, 0, 0.5);
  border-radius: 8px;
  padding: 1rem;
  margin: 1rem 0;
  color: #00ff00;
  border: 1px solid rgba(0, 255, 0, 0.3);
}

.connect-container {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.connect-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  background: rgba(0, 255, 0, 0.2);
  color: #00ff00;
  border: 1px solid #00ff00;
  border-radius: 4px;
  padding: 0.75rem 1.5rem;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.connect-btn:hover {
  background: rgba(0, 255, 0, 0.3);
  box-shadow: 0 0 10px rgba(0, 255, 0, 0.4);
}

.connect-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.wallet-icon {
  width: 24px;
  height: 24px;
}

/* 简化模式样式 */
.wallet-simplified {
  cursor: pointer;
  display: flex;
  justify-content: center;
  padding: 0.25rem;
}

.wallet-avatar {
  position: relative;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid rgba(0, 255, 0, 0.5);
  transition: all 0.3s ease;
}

.wallet-avatar:hover {
  transform: scale(1.05);
  box-shadow: 0 0 10px rgba(0, 255, 0, 0.5);
}

.wallet-avatar-icon {
  width: 22px;
  height: 22px;
}

.wallet-status-dot {
  position: absolute;
  width: 8px;
  height: 8px;
  background-color: #00ff00;
  border-radius: 50%;
  bottom: 0;
  right: 0;
  border: 1px solid #000;
}

/* 详细模式样式 */
.wallet-warning {
  margin-top: 0.5rem;
  color: orange;
  font-size: 0.9rem;
}

.wallet-warning a {
  color: #00ff00;
  text-decoration: underline;
}

.wallet-info {
  display: flex;
  align-items: center;
  justify-content: space-between;
  cursor: pointer;
  transition: all 0.3s ease;
}

.wallet-info:hover {
  background: rgba(0, 255, 0, 0.1);
}

.account-info {
  display: flex;
  flex-direction: column;
}

.address {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-family: monospace;
  font-size: 1rem;
}

.copy-btn {
  background: none;
  border: none;
  color: #00ff00;
  cursor: pointer;
  padding: 0;
  font-size: 0.8rem;
}

.balance {
  margin-top: 0.25rem;
  font-size: 1.1rem;
  font-weight: bold;
}

.disconnect-btn {
  background: rgba(255, 0, 0, 0.2);
  color: #ff3333;
  border: 1px solid #ff3333;
  border-radius: 4px;
  padding: 0.5rem 1rem;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.disconnect-btn:hover {
  background: rgba(255, 0, 0, 0.3);
  box-shadow: 0 0 10px rgba(255, 0, 0, 0.4);
}

.error-message {
  margin-top: 0.5rem;
  color: #ff3333;
  text-align: center;
  font-size: 0.9rem;
}

/* 钱包详情弹窗样式 */
.wallet-details-popup {
  position: absolute;
  top: calc(100% + 10px);
  right: 0;
  width: 300px;
  background: rgba(0, 0, 0, 0.9);
  border: 1px solid rgba(0, 255, 0, 0.5);
  border-radius: 8px;
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.6);
  z-index: 1000;
  overflow: hidden;
  animation: fadeIn 0.2s ease-out;
}

.wallet-details-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  background: rgba(0, 255, 0, 0.1);
  border-bottom: 1px solid rgba(0, 255, 0, 0.3);
}

.wallet-details-header h3 {
  margin: 0;
  color: #00ff00;
  font-size: 1.1rem;
}

.close-btn {
  background: none;
  border: none;
  color: #00ff00;
  font-size: 1.5rem;
  cursor: pointer;
  padding: 0;
  line-height: 1;
}

.wallet-details-content {
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.wallet-details-avatar {
  display: flex;
  justify-content: center;
  margin-bottom: 0.5rem;
}

.wallet-details-icon {
  width: 48px;
  height: 48px;
  background: rgba(0, 0, 0, 0.3);
  padding: 0.5rem;
  border-radius: 50%;
  border: 1px solid rgba(0, 255, 0, 0.3);
}

.wallet-details-info {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.details-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.details-item label {
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.6);
}

.details-address {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: rgba(0, 0, 0, 0.3);
  padding: 0.5rem 0.75rem;
  border-radius: 4px;
  font-family: monospace;
  font-size: 0.8rem;
  word-break: break-all;
}

.copy-details-btn {
  background: none;
  border: none;
  color: #00ff00;
  cursor: pointer;
  font-size: 0.8rem;
  padding: 0;
  margin-left: 0.5rem;
}

.details-balance, .details-network {
  background: rgba(0, 0, 0, 0.3);
  padding: 0.5rem 0.75rem;
  border-radius: 4px;
  font-size: 0.9rem;
}

.details-balance {
  color: #00ff00;
  font-weight: bold;
}

.wallet-details-actions {
  margin-top: 0.5rem;
  display: flex;
  justify-content: center;
}

.details-disconnect-btn {
  background: rgba(255, 0, 0, 0.2);
  color: #ff3333;
  border: 1px solid #ff3333;
  border-radius: 4px;
  padding: 0.5rem 1rem;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.3s ease;
  width: 100%;
}

.details-disconnect-btn:hover {
  background: rgba(255, 0, 0, 0.3);
  box-shadow: 0 0 10px rgba(255, 0, 0, 0.4);
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style> 