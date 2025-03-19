/**
 * 区块链集成服务
 * 支持MetaMask钱包、BNB Chain和Base链的NFT铸造和管理
 */

// 区块链类型
export const BLOCKCHAIN_TYPES = {
  BNB_CHAIN: 'bnb-chain',
  BASE: 'base',
  TEST: 'test' // 测试模式，不实际连接区块链
};

// 当前使用的区块链
export const CURRENT_BLOCKCHAIN = BLOCKCHAIN_TYPES.BNB_CHAIN;

// NFT状态
export const NFT_STATUS = {
  NOT_MINTED: 'not_minted',
  MINTING: 'minting',
  MINTED: 'minted',
  ERROR: 'error'
};

// 检查是否有MetaMask可用
const isMetaMaskAvailable = () => {
  return typeof window !== 'undefined' && typeof window.ethereum !== 'undefined' && window.ethereum.isMetaMask;
};

/**
 * 区块链服务类
 */
class BlockchainService {
  constructor() {
    this.initialized = false;
    this.currentChain = CURRENT_BLOCKCHAIN;
    this.connected = false;
    this.account = null;
    this.balance = '0';
    this.nfts = [];
    this.error = null;
    this.metaMaskAvailable = isMetaMaskAvailable();
  }

  /**
   * 初始化区块链服务
   * @param {string} chainType 区块链类型
   * @returns {Promise<boolean>} 是否初始化成功
   */
  async initialize(chainType = CURRENT_BLOCKCHAIN) {
    console.log(`[区块链] 初始化 ${chainType} 连接`);
    
    if (this.initialized) {
      console.log('[区块链] 已经初始化，跳过');
      return true;
    }
    
    try {
      this.metaMaskAvailable = isMetaMaskAvailable();
      
      if (this.metaMaskAvailable) {
        console.log('[区块链] 检测到MetaMask钱包');
        
        // 监听账户变化
        window.ethereum.on('accountsChanged', (accounts) => {
          if (accounts.length === 0) {
            // 用户断开了钱包
            this.connected = false;
            this.account = null;
            this.balance = '0';
            console.log('[区块链] 用户断开了钱包连接');
          } else {
            // 用户切换了账户
            this.account = accounts[0];
            this.updateBalance();
            console.log(`[区块链] 账户已切换: ${this.account}`);
          }
        });
        
        // 监听链变化
        window.ethereum.on('chainChanged', (chainId) => {
          console.log(`[区块链] 链已变更: ${chainId}`);
          window.location.reload(); // 刷新应用以适应新链
        });
      } else {
        // 无MetaMask使用模拟实现
        console.log('[区块链] 未检测到MetaMask，使用模拟实现');
      }
      
      this.currentChain = chainType;
      this.initialized = true;
      
      // 检查是否已连接
      if (this.metaMaskAvailable) {
        const accounts = await window.ethereum.request({ method: 'eth_accounts' });
        if (accounts.length > 0) {
          this.account = accounts[0];
          this.connected = true;
          await this.updateBalance();
          console.log(`[区块链] 已连接到现有账户: ${this.account}`);
        }
      }
      
      console.log(`[区块链] ${chainType} 初始化成功`);
      return true;
    } catch (error) {
      console.error('[区块链] 初始化失败:', error);
      this.error = `初始化失败: ${error.message}`;
      return false;
    }
  }
  
  /**
   * 连接钱包
   * @returns {Promise<Object>} 连接结果
   */
  async connectWallet() {
    if (!this.initialized) {
      await this.initialize();
    }
    
    console.log('[区块链] 连接钱包');
    
    try {
      if (this.metaMaskAvailable) {
        // 使用MetaMask连接
        const accounts = await window.ethereum.request({ method: 'eth_requestAccounts' });
        
        if (accounts.length === 0) {
          throw new Error('用户拒绝了钱包连接请求');
        }
        
        this.connected = true;
        this.account = accounts[0];
        
        // 获取余额
        await this.updateBalance();
        
        console.log(`[区块链] 已连接MetaMask钱包: ${this.account}, 余额: ${this.balance} ${this.getChainCurrency()}`);
      } else {
        // 模拟钱包连接
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        this.connected = true;
        this.account = '0x' + Math.random().toString(16).slice(2, 12) + Math.random().toString(16).slice(2, 12);
        this.balance = (Math.random() * 10).toFixed(4);
        
        console.log(`[区块链] 已连接模拟钱包: ${this.account}, 余额: ${this.balance} ${this.getChainCurrency()}`);
      }
      
      return {
        success: true,
        account: this.account,
        balance: this.balance,
        currency: this.getChainCurrency()
      };
    } catch (error) {
      console.error('[区块链] 连接钱包失败:', error);
      this.error = `连接钱包失败: ${error.message}`;
      this.connected = false;
      
      return {
        success: false,
        error: this.error
      };
    }
  }
  
  /**
   * 更新余额
   */
  async updateBalance() {
    if (!this.connected || !this.account) return;
    
    try {
      if (this.metaMaskAvailable) {
        // 使用MetaMask获取余额
        const balanceHex = await window.ethereum.request({
          method: 'eth_getBalance',
          params: [this.account, 'latest']
        });
        
        // 将16进制余额转换为ETH（18位小数）
        const balanceWei = parseInt(balanceHex, 16);
        this.balance = (balanceWei / 1e18).toFixed(4);
      } else {
        // 模拟余额
        this.balance = (Math.random() * 10).toFixed(4);
      }
    } catch (error) {
      console.error('[区块链] 获取余额失败:', error);
      this.balance = '0';
    }
  }
  
  /**
   * 断开钱包连接
   * @returns {Promise<boolean>} 是否断开成功
   */
  async disconnectWallet() {
    console.log('[区块链] 断开钱包连接');
    
    try {
      // MetaMask没有提供断开连接的API，我们只能在前端状态中断开
      this.connected = false;
      this.account = null;
      this.balance = '0';
      
      return {
        success: true
      };
    } catch (error) {
      console.error('[区块链] 断开钱包失败:', error);
      return {
        success: false,
        error: error.message
      };
    }
  }
  
  /**
   * 获取连接状态
   */
  getConnectionStatus() {
    return {
      initialized: this.initialized,
      connected: this.connected,
      account: this.account,
      balance: this.balance,
      chain: this.currentChain,
      currency: this.getChainCurrency(),
      metaMaskAvailable: this.metaMaskAvailable
    };
  }
  
  /**
   * 获取当前链的货币名称
   */
  getChainCurrency() {
    switch (this.currentChain) {
      case 'bnb-chain':
        return 'BNB';
      case 'base':
        return 'ETH';
      case 'test':
        return 'tBNB';
      default:
        return 'ETH';
    }
  }
  
  /**
   * 铸造NFT
   */
  async mintNFT(metadata) {
    if (!this.connected) {
      throw new Error('未连接钱包');
    }
    
    console.log('[区块链] 开始铸造NFT:', metadata);
    
    try {
      // 当前只是模拟铸造
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // 生成随机NFT地址
      const nftAddress = `0x${Math.random().toString(16).substr(2, 40)}`;
      
      console.log('[区块链] NFT铸造成功:', nftAddress);
      return {
        success: true,
        nftAddress,
        transactionHash: `0x${Math.random().toString(16).substr(2, 64)}`,
        metadata
      };
    } catch (error) {
      console.error('[区块链] 铸造NFT失败:', error);
      return {
        success: false,
        error: error.message
      };
    }
  }
}

// 导出区块链服务实例
const blockchainService = new BlockchainService();
export default blockchainService; 