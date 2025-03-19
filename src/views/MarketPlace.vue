<template>
  <div class="marketplace">
    <h1>智能体市场</h1>
    
    <div class="market-metrics">
      <div class="metric-card">
        <h3>总市值</h3>
        <p class="value">{{ totalMarketValue }}ETH</p>
      </div>
      <div class="metric-card">
        <h3>24h成交量</h3>
        <p class="value">{{ volume24h }}ETH</p>
      </div>
      <div class="metric-card">
        <h3>智能体总数</h3>
        <p class="value">{{ agents.length }}</p>
      </div>
    </div>
    
    <div class="filter-bar">
      <div class="search-box">
        <input type="text" v-model="searchQuery" placeholder="搜索智能体..." />
      </div>
      <div class="sort-options">
        <span>排序: </span>
        <select v-model="sortOption">
          <option value="value-desc">市值 (高到低)</option>
          <option value="value-asc">市值 (低到高)</option>
          <option value="date-desc">创建日期 (新到旧)</option>
          <option value="date-asc">创建日期 (旧到新)</option>
        </select>
      </div>
    </div>
    
    <div class="agents-table">
      <table>
        <thead>
          <tr>
            <th>头像</th>
            <th>名称</th>
            <th>描述</th>
            <th>创建日期</th>
            <th>估值</th>
            <th>NFT状态</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="agent in sortedAgents" :key="agent.id">
            <td>
              <div class="agent-avatar">
                <img :src="agent.avatar || './default-avatar.png'" alt="头像" />
              </div>
            </td>
            <td>{{ agent.name }}</td>
            <td class="description-cell">{{ agent.description }}</td>
            <td>{{ formatDate(agent.createdAt) }}</td>
            <td class="value-cell">{{ formatValue(agent.price) }} ETH</td>
            <td>
              <span :class="['nft-status', getNftStatusClass(agent)]">
                {{ agent.nftMinted ? 'NFT已铸造' : '未铸造' }}
              </span>
            </td>
            <td>
              <div class="action-buttons">
                <router-link :to="'/agent/' + agent.id" class="action-btn view-btn">
                  查看
                </router-link>
                <button class="action-btn buy-btn" @click="handleBuy(agent)">
                  购买 {{ formatValue(agent.price) }}ETH
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useAgentStore } from '../store/agents';
import { storeToRefs } from 'pinia';
import { useRouter } from 'vue-router';

const router = useRouter();
const agentStore = useAgentStore();
const { agents } = storeToRefs(agentStore);

// 过滤和排序
const searchQuery = ref('');
const sortOption = ref('value-desc');

// 计算市场统计数据
const totalMarketValue = ref('245.8');
const volume24h = ref('12.5');

// 根据搜索和排序过滤智能体
const sortedAgents = computed(() => {
  // 添加市值和搜索功能
  let filteredAgents = agents.value.map(agent => ({
    ...agent,
    marketValue: agent.marketValue || randomMarketValue(agent.id)
  }));
  
  // 搜索过滤
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase();
    filteredAgents = filteredAgents.filter(agent => 
      agent.name.toLowerCase().includes(query) || 
      agent.description.toLowerCase().includes(query)
    );
  }
  
  // 排序
  return filteredAgents.sort((a, b) => {
    switch (sortOption.value) {
      case 'value-desc':
        return b.marketValue - a.marketValue;
      case 'value-asc':
        return a.marketValue - b.marketValue;
      case 'date-desc':
        return new Date(b.createdAt) - new Date(a.createdAt);
      case 'date-asc':
        return new Date(a.createdAt) - new Date(b.createdAt);
      default:
        return 0;
    }
  });
});

// 格式化日期
function formatDate(dateString) {
  try {
    const date = new Date(dateString);
    return date.toLocaleDateString('zh-CN');
  } catch (e) {
    return dateString;
  }
}

// 格式化市值
function formatValue(value) {
  return Number(value).toFixed(2);
}

// 处理购买按钮点击
async function handleBuy(agent) {
  try {
    // 检查钱包是否连接
    const { ethereum } = window;
    if (!ethereum || !ethereum.isMetaMask) {
      alert('请安装并连接MetaMask钱包以购买智能体');
      return;
    }
    
    // 检查是否已连接账户
    const accounts = await ethereum.request({ method: 'eth_accounts' });
    if (!accounts || accounts.length === 0) {
      const newAccounts = await ethereum.request({ method: 'eth_requestAccounts' });
      if (!newAccounts || newAccounts.length === 0) {
        alert('请连接MetaMask钱包以继续购买');
        return;
      }
    }
    
    // 确认购买
    if (!confirm(`确认以 ${formatValue(agent.price)} ETH 购买智能体 "${agent.name}"?`)) {
      return;
    }
    
    // 开始购买流程
    alert(`交易已发起，等待处理...\n\n确认后，将自动为您分配智能体 "${agent.name}"\n\n在实际环境中，这里会调用智能合约执行转账和NFT铸造。`);
    
    // 购买成功
    setTimeout(() => {
      alert(`恭喜！您已成功购买智能体 "${agent.name}"。`);
    }, 1500);
    
  } catch (error) {
    console.error('购买智能体失败:', error);
    alert(`购买失败: ${error.message || '未知错误'}`);
  }
}

// 获取NFT状态样式
function getNftStatusClass(agent) {
  return {
    'minted': agent.nftMinted,
    'not-minted': !agent.nftMinted
  };
}

// 随机生成市值（实际项目中应该从市场数据API获取）
function randomMarketValue(id) {
  // 使用固定的种子来确保每次刷新页面时相同ID得到相同的值
  const seed = id * 1000;
  const rand = Math.sin(seed) * 10000;
  return Math.abs(rand % 10) + 0.5; // 0.5 - 10.5 ETH
}
</script>

<style scoped>
.marketplace {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

h1 {
  text-align: center;
  margin-bottom: 2rem;
  color: var(--primary-color);
  text-shadow: var(--text-shadow);
}

.market-metrics {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  margin-bottom: 2rem;
}

.metric-card {
  background: rgba(0, 255, 0, 0.05);
  border: 1px solid rgba(0, 255, 0, 0.3);
  border-radius: 8px;
  padding: 1.5rem;
  text-align: center;
}

.light-mode .metric-card {
  background: rgba(0, 102, 51, 0.05);
  border: 1px solid rgba(0, 102, 51, 0.3);
}

.metric-card h3 {
  color: var(--text-secondary);
  font-size: 0.9rem;
  margin-bottom: 0.5rem;
}

.metric-card .value {
  color: var(--primary-color);
  font-size: 1.8rem;
  font-weight: bold;
  text-shadow: var(--text-shadow);
}

.filter-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.search-box input {
  background: var(--input-bg);
  border: 1px solid var(--border-color);
  color: var(--input-text);
  padding: 0.5rem 1rem;
  width: 300px;
  border-radius: 4px;
}

.search-box input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 10px rgba(0, 255, 0, 0.3);
}

.light-mode .search-box input:focus {
  box-shadow: 0 0 10px rgba(0, 102, 51, 0.3);
}

.sort-options select {
  background: var(--input-bg);
  border: 1px solid var(--border-color);
  color: var(--input-text);
  padding: 0.5rem 1rem;
  border-radius: 4px;
}

.agents-table {
  width: 100%;
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
  background: var(--bg-lighter);
  border: 1px solid var(--border-color);
}

th, td {
  padding: 1rem;
  text-align: left;
  border-bottom: 1px solid var(--border-color);
}

th {
  color: var(--primary-color);
  background: rgba(0, 255, 0, 0.1);
  text-transform: uppercase;
  font-size: 0.8rem;
}

.light-mode th {
  background: rgba(0, 102, 51, 0.05);
}

.agent-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  overflow: hidden;
  border: 1px solid var(--primary-color);
}

.agent-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.description-cell {
  max-width: 200px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  color: var(--text-color);
}

.value-cell {
  color: var(--primary-color);
  font-weight: bold;
}

.nft-status {
  padding: 0.3rem 0.6rem;
  border-radius: 4px;
  font-size: 0.8rem;
}

.nft-status.minted {
  background: rgba(0, 255, 0, 0.2);
  color: var(--primary-color);
  border: 1px solid rgba(0, 255, 0, 0.4);
}

.light-mode .nft-status.minted {
  background: rgba(0, 102, 51, 0.1);
  border: 1px solid rgba(0, 102, 51, 0.3);
}

.nft-status.not-minted {
  background: rgba(255, 0, 0, 0.1);
  color: #ff6666;
  border: 1px solid rgba(255, 0, 0, 0.3);
}

.action-buttons {
  display: flex;
  gap: 0.5rem;
}

.action-btn {
  padding: 0.4rem 0.8rem;
  font-size: 0.8rem;
  border-radius: 4px;
  display: inline-block;
  text-decoration: none;
  transition: all 0.3s ease;
  background: none;
  cursor: pointer;
}

.view-btn {
  color: var(--primary-color);
  border: 1px solid var(--primary-color);
  margin-right: 0.5rem;
}

.buy-btn {
  color: #fff;
  background-color: var(--primary-color);
  border: 1px solid var(--primary-color);
}

.buy-btn:hover {
  background-color: rgba(0, 255, 0, 0.8);
}

.light-mode .buy-btn {
  background-color: var(--light-primary-color);
  border: 1px solid var(--light-primary-color);
}

.light-mode .buy-btn:hover {
  background-color: rgba(0, 102, 51, 0.8);
}

.dialog-btn {
  background: rgba(0, 180, 255, 0.1);
  border-color: rgba(0, 180, 255, 0.3);
  color: rgb(0, 180, 255);
}

.light-mode .dialog-btn {
  background: rgba(0, 102, 153, 0.05);
  border-color: rgba(0, 102, 153, 0.3);
  color: rgb(0, 102, 153);
}

.dialog-btn:hover {
  background: rgba(0, 180, 255, 0.2);
  box-shadow: 0 0 5px rgba(0, 180, 255, 0.3);
}

.light-mode .dialog-btn:hover {
  background: rgba(0, 102, 153, 0.1);
  box-shadow: 0 0 5px rgba(0, 102, 153, 0.3);
}
</style> 