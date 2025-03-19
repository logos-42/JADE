<template>
  <div class="agent-detail">
    <div class="header">
      <h1>{{ agent ? agent.name : '加载中...' }}</h1>
      <router-link to="/agents" class="back-btn">返回列表</router-link>
    </div>
    
    <div class="content" v-if="agent">
      <div class="agent-header">
        <div class="agent-avatar">
          <img :src="agent.avatar || './default-avatar.png'" alt="智能体头像">
        </div>
        <div class="agent-title">
          <h2>{{ agent.name }}</h2>
          <div class="agent-id">ID: {{ agent.id }}</div>
        </div>
      </div>
      
      <div class="info-section">
        <h3>基本信息</h3>
        <div class="info-grid">
          <div class="info-item">
            <label>描述</label>
            <p>{{ agent.description }}</p>
          </div>
          <div class="info-item">
            <label>创建时间</label>
            <span>{{ formatDate(agent.createdAt) }}</span>
          </div>
          <div v-if="agent.nftMinted" class="info-item">
            <label>NFT地址</label>
            <div class="nft-address">{{ agent.nftAddress }}</div>
          </div>
        </div>
      </div>
      
      <div class="conversation-section">
        <h3>对话选项</h3>
        <div class="dialog-options">
          <div class="dialog-direct">
            <h4>直接对话</h4>
            <p>与此智能体进行一对一对话</p>
            <button @click="startDirectDialog" class="action-btn">
              开始对话
            </button>
          </div>
          
          <div class="dialog-multi">
            <h4>选择对话对象</h4>
            <p>选择另一个智能体，让两个智能体互相对话</p>
            <div class="agent-selector">
              <select v-model="selectedAgentId">
                <option value="">-- 选择智能体 --</option>
                <option 
                  v-for="otherAgent in otherAgents" 
                  :key="otherAgent.id" 
                  :value="otherAgent.id"
                >
                  {{ otherAgent.name }}
                </option>
              </select>
              <button 
                @click="startMultiDialog" 
                class="action-btn" 
                :disabled="!selectedAgentId"
              >
                开始多方对话
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <div class="nft-section" v-if="!agent.nftMinted">
        <h3>区块链功能</h3>
        <div class="blockchain-functions">
          <div class="wallet-binding" v-if="!agent.walletAddress">
            <h4>绑定钱包</h4>
            <p>将此智能体与您的MetaMask钱包绑定，以启用区块链功能</p>
            
            <div class="wallet-status" v-if="isWalletConnected">
              <div class="wallet-info">
                <div class="wallet-address">当前钱包: {{ formatAddress(walletAccount) }}</div>
                <div class="wallet-balance">{{ walletBalance }} {{ walletCurrency }}</div>
              </div>
              <button 
                @click="bindWalletToAgent" 
                class="action-btn" 
                :disabled="isBindingWallet"
              >
                {{ isBindingWallet ? '绑定中...' : '绑定钱包' }}
              </button>
            </div>
            
            <div class="wallet-connect-wrapper" v-else>
              <p class="wallet-notice">请先连接MetaMask钱包</p>
              <WalletConnect @wallet-connected="onWalletConnected" />
            </div>
          </div>
          
          <div class="wallet-bound" v-else>
            <h4>已绑定钱包</h4>
            <div class="bound-wallet-info">
              <p>绑定地址: {{ formatAddress(agent.walletAddress) }}</p>
              <p>绑定时间: {{ formatDate(agent.walletBindTime) }}</p>
            </div>
          </div>
          
          <div class="nft-minting" v-if="agent.walletAddress && !agent.nftMinted">
            <h4>NFT铸造</h4>
            <p>将此智能体铸造为区块链上的NFT，获得唯一所有权</p>
            <button 
              @click="mintNFT" 
              class="mint-btn" 
              :disabled="isMinting"
            >
              {{ isMinting ? '铸造中...' : '铸造NFT' }}
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <div class="error" v-else-if="!loading">
      <p>找不到该智能体信息</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useAgentStore } from '../store/agents';
import blockchainService from '../services/blockchain';
import WalletConnect from '../components/WalletConnect.vue';

const route = useRoute();
const router = useRouter();
const agentStore = useAgentStore();
const loading = ref(true);
const selectedAgentId = ref('');
const isMinting = ref(false);

const agent = computed(() => {
  return agentStore.getAgentById(parseInt(route.params.id));
});

// 获取其他智能体（排除当前智能体）
const otherAgents = computed(() => {
  if (!agent.value) return [];
  return agentStore.agents.filter(a => a.id !== agent.value.id);
});

// 钱包状态
const isWalletConnected = ref(false);
const walletAccount = ref('');
const walletBalance = ref('0');
const walletCurrency = ref('ETH');
const isBindingWallet = ref(false);

// 更新钱包状态
const updateWalletStatus = () => {
  const status = blockchainService.getConnectionStatus();
  isWalletConnected.value = status.connected;
  walletAccount.value = status.account;
  walletBalance.value = status.balance;
  walletCurrency.value = status.currency;
};

// 钱包连接时的回调
const onWalletConnected = () => {
  updateWalletStatus();
};

// 绑定钱包到智能体
const bindWalletToAgent = async () => {
  if (!isWalletConnected.value || !walletAccount.value) {
    alert('请先连接钱包');
    return;
  }
  
  isBindingWallet.value = true;
  
  try {
    // 更新智能体信息，添加钱包地址
    const updateResult = agentStore.updateAgent(agent.value.id, {
      walletAddress: walletAccount.value,
      walletBindTime: new Date().toISOString()
    });
    
    if (updateResult) {
      alert('钱包绑定成功！现在您可以铸造NFT了。');
    } else {
      throw new Error('绑定钱包失败');
    }
  } catch (error) {
    alert('绑定钱包失败: ' + error.message);
  } finally {
    isBindingWallet.value = false;
  }
};

// 格式化钱包地址显示
const formatAddress = (address) => {
  if (!address) return '';
  return address.slice(0, 6) + '...' + address.slice(-4);
};

// 格式化日期
function formatDate(dateString) {
  try {
    const date = new Date(dateString);
    return date.toLocaleDateString('zh-CN');
  } catch (e) {
    return dateString;
  }
}

// 开始多智能体对话
function startMultiDialog() {
  if (!selectedAgentId.value) return;
  
  // 创建对话
  const conversation = agentStore.createConversation(
    parseInt(agent.value.id),
    parseInt(selectedAgentId.value)
  );
  
  if (conversation.success) {
    // 导航到对话页面
    router.push(`/dialog/${agent.value.id}?partner=${selectedAgentId.value}`);
  } else {
    alert('创建对话失败: ' + conversation.message);
  }
}

// 铸造NFT
const mintNFT = async () => {
  if (!agent.value) return;
  
  // 检查钱包是否已绑定
  if (!agent.value.walletAddress) {
    alert('请先绑定钱包后再铸造NFT');
    return;
  }
  
  isMinting.value = true;
  
  try {
    const result = await agentStore.mintAgentNFT(agent.value.id, agent.value.walletAddress);
    
    if (result.success) {
      alert(`智能体NFT铸造成功!\n地址: ${result.nftAddress}`);
    } else {
      throw new Error(result.message);
    }
  } catch (error) {
    alert('铸造NFT失败: ' + error.message);
  } finally {
    isMinting.value = false;
  }
}

// 开始直接对话
function startDirectDialog() {
  if (!agent.value) return;
  
  // 创建对话
  const conversation = agentStore.createConversation(
    parseInt(agent.value.id),
    parseInt(agent.value.id)
  );
  
  if (conversation.success) {
    // 导航到对话页面
    router.push(`/dialog/${agent.value.id}`);
  } else {
    alert('创建对话失败: ' + conversation.message);
  }
}

onMounted(() => {
  loading.value = false;
  // 获取钱包状态
  updateWalletStatus();
});
</script>

<style scoped>
.agent-detail {
  padding: 2rem;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

h1 {
  color: var(--primary-color);
  text-shadow: var(--text-shadow);
  margin: 0;
}

.back-btn {
  padding: 0.5rem 1rem;
  background: rgba(0, 255, 0, 0.1);
  border: 1px solid var(--primary-color);
  color: var(--primary-color);
  text-decoration: none;
  border-radius: 4px;
  transition: all 0.3s ease;
}

.light-mode .back-btn {
  background: rgba(0, 102, 51, 0.05);
}

.back-btn:hover {
  background: rgba(0, 255, 0, 0.2);
  box-shadow: 0 0 10px rgba(0, 255, 0, 0.3);
}

.light-mode .back-btn:hover {
  background: rgba(0, 102, 51, 0.1);
  box-shadow: 0 0 10px rgba(0, 102, 51, 0.3);
}

.content {
  background: rgba(0, 255, 0, 0.1);
  border: 1px solid var(--primary-color);
  border-radius: 8px;
  padding: 2rem;
}

.light-mode .content {
  background: rgba(0, 102, 51, 0.05);
}

.agent-header {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  margin-bottom: 2rem;
  padding-bottom: 2rem;
  border-bottom: 1px solid rgba(0, 255, 0, 0.3);
}

.light-mode .agent-header {
  border-bottom: 1px solid rgba(0, 102, 51, 0.3);
}

.agent-avatar {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  overflow: hidden;
  border: 3px solid var(--primary-color);
  box-shadow: 0 0 15px rgba(0, 255, 0, 0.3);
  background: var(--bg-color);
}

.light-mode .agent-avatar {
  box-shadow: 0 0 15px rgba(0, 102, 51, 0.3);
}

.agent-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.agent-title {
  flex: 1;
}

.agent-title h2 {
  color: var(--primary-color);
  margin: 0 0 0.5rem 0;
  font-size: 1.8rem;
}

.agent-id {
  color: var(--text-secondary);
  font-family: 'Share Tech Mono', monospace;
}

.info-section h3 {
  color: var(--primary-color);
  margin-bottom: 1.5rem;
  font-size: 1.3rem;
}

.info-grid {
  display: grid;
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.info-item label {
  color: var(--primary-color);
  font-size: 0.9rem;
}

.info-item span {
  color: var(--text-color);
  font-size: 1.1rem;
}

.conversation-section {
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 1px solid rgba(0, 255, 0, 0.3);
}

.light-mode .conversation-section {
  border-top: 1px solid rgba(0, 102, 51, 0.3);
}

.dialog-options {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
}

.dialog-direct, .dialog-multi {
  background: rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(0, 255, 0, 0.2);
  border-radius: 8px;
  padding: 1.5rem;
}

.light-mode .dialog-direct, .light-mode .dialog-multi {
  background: rgba(240, 240, 240, 0.5);
  border: 1px solid rgba(0, 102, 51, 0.2);
}

.dialog-direct h4, .dialog-multi h4 {
  color: var(--primary-color);
  margin-bottom: 0.5rem;
}

.dialog-direct p, .dialog-multi p {
  color: var(--text-secondary);
  margin-bottom: 1.5rem;
  font-size: 0.9rem;
}

.agent-selector {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.agent-selector select {
  background: var(--input-bg);
  border: 1px solid rgba(0, 255, 0, 0.3);
  color: var(--input-text);
  padding: 0.8rem;
  border-radius: 4px;
  font-size: 1rem;
  width: 100%;
}

.light-mode .agent-selector select {
  border: 1px solid rgba(0, 102, 51, 0.3);
}

.agent-selector select:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 10px rgba(0, 255, 0, 0.3);
}

.light-mode .agent-selector select:focus {
  box-shadow: 0 0 10px rgba(0, 102, 51, 0.3);
}

.nft-section {
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 1px solid rgba(0, 255, 0, 0.3);
}

.light-mode .nft-section {
  border-top: 1px solid rgba(0, 102, 51, 0.3);
}

.nft-address {
  font-family: 'Share Tech Mono', monospace;
  background: rgba(0, 0, 0, 0.3);
  padding: 0.5rem 1rem;
  border-radius: 4px;
  word-break: break-all;
}

.light-mode .nft-address {
  background: rgba(240, 240, 240, 0.5);
  color: var(--text-color);
}

.mint-btn {
  padding: 0.8rem 1.5rem;
  background: rgba(0, 255, 234, 0.2);
  border: 1px solid rgba(0, 255, 234, 0.5);
  color: rgb(0, 255, 234);
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-top: 1rem;
}

.light-mode .mint-btn {
  background: rgba(0, 150, 136, 0.1);
  border: 1px solid rgba(0, 150, 136, 0.5);
  color: rgb(0, 150, 136);
}

.mint-btn:hover {
  background: rgba(0, 255, 234, 0.3);
  box-shadow: 0 0 10px rgba(0, 255, 234, 0.3);
}

.light-mode .mint-btn:hover {
  background: rgba(0, 150, 136, 0.2);
  box-shadow: 0 0 10px rgba(0, 150, 136, 0.3);
}

.mint-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .dialog-options {
    grid-template-columns: 1fr;
  }
  
  .agent-header {
    flex-direction: column;
    text-align: center;
  }
}

.blockchain-functions {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  background: rgba(0, 255, 0, 0.05);
  border-radius: 8px;
  padding: 1.5rem;
  margin-top: 1rem;
}

.light-mode .blockchain-functions {
  background: rgba(0, 102, 51, 0.03);
}

.wallet-binding, .wallet-bound, .nft-minting {
  border-bottom: 1px solid rgba(0, 255, 0, 0.2);
  padding-bottom: 1.5rem;
}

.light-mode .wallet-binding, .light-mode .wallet-bound, .light-mode .nft-minting {
  border-bottom: 1px solid rgba(0, 102, 51, 0.2);
}

.wallet-binding:last-child, .wallet-bound:last-child, .nft-minting:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.wallet-binding h4, .wallet-bound h4, .nft-minting h4 {
  color: var(--primary-color);
  margin-bottom: 0.5rem;
}

.wallet-status {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 6px;
  padding: 1rem;
  margin-top: 1rem;
}

.light-mode .wallet-status {
  background: rgba(240, 240, 240, 0.5);
}

.wallet-info {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.wallet-address {
  font-family: monospace;
  font-size: 0.9rem;
}

.wallet-balance {
  font-weight: bold;
  color: var(--primary-color);
}

.wallet-notice {
  margin-bottom: 1rem;
  color: #ffcc00;
}

.light-mode .wallet-notice {
  color: #996600;
}

.bound-wallet-info {
  background: rgba(0, 0, 0, 0.3);
  border-radius: 6px;
  padding: 1rem;
  margin-top: 1rem;
}

.light-mode .bound-wallet-info {
  background: rgba(240, 240, 240, 0.5);
}

.bound-wallet-info p {
  margin: 0.5rem 0;
  font-size: 0.9rem;
}

.wallet-connect-wrapper {
  margin-top: 1rem;
}

.action-btn {
  padding: 0.5rem 1rem;
  background: rgba(0, 255, 0, 0.2);
  border: 1px solid var(--primary-color);
  color: var(--primary-color);
  text-decoration: none;
  border-radius: 4px;
  transition: all 0.3s ease;
  cursor: pointer;
}

.light-mode .action-btn {
  background: rgba(0, 102, 51, 0.1);
}

.action-btn:hover {
  background: rgba(0, 255, 0, 0.3);
  box-shadow: 0 0 10px rgba(0, 255, 0, 0.3);
}

.light-mode .action-btn:hover {
  background: rgba(0, 102, 51, 0.2);
  box-shadow: 0 0 10px rgba(0, 102, 51, 0.3);
}

.action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style> 